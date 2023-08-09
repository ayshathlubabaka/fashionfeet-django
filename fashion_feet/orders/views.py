import datetime
from django.shortcuts import render, redirect
from cart.models import CartItem
from .models import Order, OrderProduct
from .forms import OrderForm
from django.db import transaction
from django.contrib import messages
from home.models import Product

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# Create your views here.


def payments(request):
    order_number = request.session.get('order_number')
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
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

        product = Product.objects.get(id=item.product_id)
        product.stock = item.quantity
        product.save()

    CartItem.objects.filter(user = request.user).delete()

    mail_subject = 'Please activate your account'
    message = render_to_string('order_recieved_email.html',{
        'user' : request.user,
        'order' : order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    return render(request, 'order_complete.html')


def place_order(request, total=0, quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    delivery_charge = 0
    discount = 0
    grand_total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    delivery_charge = 30
    discount = (2 * total)/100
    grand_total = total + delivery_charge - discount
    
    if request.method == 'POST':
        print('post method')
        form = OrderForm(request.POST)
        print(form.errors)
        if form.is_valid():
            print('form is valid')
            data = Order()
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
            data.order_total = grand_total
            data.delivery_charge = delivery_charge
            data.discount = discount
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

            order = Order.objects.get(user = current_user, is_ordered = False, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total': total,
                'delivery_charge' : delivery_charge,
                'discount' : discount,
                'grand_total' : grand_total,
            }
            request.session['order_number'] = order_number
            return render(request, 'payments.html' , context)
    
    return render(request, 'checkout.html', {'form': form, 'total': total, 'quantity': quantity})