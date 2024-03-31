import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from cart.models import CartItem
from .models import Order, OrderProduct, Payment
from .forms import OrderForm

from home.models import Coupon
from accounts.models import UserProfile

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import json
# Create your views here.


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']

    )
    payment.save()
    order.payment = payment
    
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        for variation in product_variation:
            variation.stock -= item.quantity
            variation.save()

    CartItem.objects.filter(user = request.user).delete()

    mail_subject = 'THANKYOU FOR YOUR ORDER'
    message = render_to_string('order_recieved_email.html',{
        'user' : request.user,
        'order' : order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }


    return JsonResponse(data)


def place_order(request, total=0, quantity = 0):
    try:
        user_profile = UserProfile.objects.get(user = request.user)
    except UserProfile.DoesNotExist:
        pass
    data = Order()

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    
    delivery_charge = 30
    offer_discount = 0
    coupon_discount = 0
    grand_total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if request.method == 'POST':
        selected_address = request.POST.get('address_option')
        
        if selected_address == 'new':
            form = OrderForm(request.POST)
            if form.is_valid():
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
        else:
            data.user = user_profile.user
            data.first_name = user_profile.user.first_name
            data.last_name = user_profile.user.last_name
            data.phone = user_profile.user.phone_number
            data.email = user_profile.user.email
            data.address_line_1 = user_profile.address_line_1
            data.address_line_2 = user_profile.address_line_2
            data.city = user_profile.city
            data.state = user_profile.state
            data.country = user_profile.country

        
        data.delivery_charge = delivery_charge

        selected_offer = request.POST.get('selected_offer') 

        if selected_offer:
            offer_discount = request.POST.get(f'{selected_offer}_discount')
            offer_discount = float(offer_discount)
        else:
            offer_discount = 0
        
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code, is_expired=False)
            coupon_discount = coupon.discount_price
        except Coupon.DoesNotExist:
            pass

        data.offer_discount = offer_discount
        data.coupon_discount = coupon_discount
        data.order_total = total + data.delivery_charge - (data.offer_discount + data.coupon_discount)
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        discount = coupon_discount + offer_discount
        grand_total = total + delivery_charge - discount

        order = Order.objects.get(user = request.user, is_ordered = False, order_number=order_number)
        context = {
            'order' : order,
            'cart_items' : cart_items,
            'total': total,
            'delivery_charge' : delivery_charge,
            'offer_discount' : offer_discount,
            'coupon_discount' : coupon_discount,
            'grand_total' : grand_total,
            'coupon_code': coupon_code,
            'user_profile' : user_profile if user_profile else None
        }
        request.session['order_number'] = order_number
        return render(request, 'payments.html' , context)

    return render(request, 'checkout.html', {'form': form, 'total': total, 'quantity': quantity, 'user_profile' : user_profile})

def order_complete(request):
    
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        payment = Payment.objects.get(payment_id=transID)
        discount = 0
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        discount = (order.offer_discount + order.coupon_discount)
        
        grand_total = subtotal+order.delivery_charge-(discount)


        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
            'grand_total' : grand_total,  
        }
        return render(request, 'order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
