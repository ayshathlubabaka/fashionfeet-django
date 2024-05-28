from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account
from django.db.models import Sum
from datetime import date, timedelta
from orders.models import Order
from home.models import Category, Product, Variation, Coupon, MinimumPurchaseOffer, CategoryOffer
from django.contrib.auth.models import auth
from django.contrib import messages
from orders.models import Order, OrderProduct
from django.contrib.auth import logout
import decimal
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View
import base64
import os
import uuid
import json
from django.db.models import Count
from django.http import JsonResponse
from django.utils.encoding import smart_str
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user and user.is_admin:
            auth.login(request, user)
            return redirect('admin_dash')
        else:
            
            messages.info(request, 'invalid credentials')
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')

@login_required(login_url = 'admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url = 'admin_login')
def admin_lte(request):
    return render(request, 'adminlte/index.html')


def sales_report(request):
    
    total_sales = Order.objects.filter(is_ordered=True).aggregate(total_sales=Sum('order_total'))['total_sales']

    category_sales = Category.objects.annotate(sales_revenue=Sum('product__orderproduct__product_price'))

    product_sales = Product.objects.annotate(sales_revenue=Sum('orderproduct__product_price'))

    start_date = date.today() - timedelta(days=7)

    daily_sales = Order.objects.filter(is_ordered=True, created_at__gte=start_date).values('created_at__date').annotate(daily_sales=Sum('order_total')).order_by('-created_at__date')
    
    previous_day_sales = Order.objects.filter(is_ordered=True, created_at__date=start_date - timedelta(days=1)).aggregate(previous_day_sales=Sum('order_total'))['previous_day_sales']
    
    increase_percentage = ((decimal.Decimal(total_sales) - decimal.Decimal(previous_day_sales)) / decimal.Decimal(previous_day_sales)) * 100 if previous_day_sales else 0

    orders = Order.objects.all()
    print(orders)
    context = {
        'total_sales': total_sales,
        'category_sales': category_sales,
        'product_sales': product_sales,
        'daily_sales': daily_sales,
        'increase_percentage': increase_percentage,
        'orders' : orders,
    }

    return render(request, 'sales_report.html', context)

@login_required(login_url = 'admin_login')
def admin_dash(request):

    products = Product.objects.annotate(num_orders=Count('orderproduct'))

    total_users = Account.objects.count()
    total_users = int(total_users)-1
    total_orders = Order.objects.count()
    
    total_sales = Order.objects.filter(is_ordered=True).aggregate(total_sales=Sum('order_total'))['total_sales']

    
    category_sales = Category.objects.annotate(sales_revenue=Sum('product__orderproduct__product_price')).values('category_name', 'sales_revenue')

    
    category_sales_list = []
    for category_sale in category_sales:
        category_sale_dict = {
            'category_name': category_sale['category_name'],
            'sales_revenue': category_sale['sales_revenue'],
        }
        category_sales_list.append(category_sale_dict)


    product_sales = Product.objects.annotate(sales_revenue=Sum('orderproduct__product_price')).values('product_name', 'sales_revenue')

    start_date = date.today() - timedelta(days=7)
    daily_sales = Order.objects.filter(is_ordered=True, created_at__gte=start_date).values('created_at__date').annotate(daily_sales=Sum('order_total')).order_by('created_at__date')


    daily_sales_list = []
    for daily_sale in daily_sales:
        daily_sale_dict = {
            'created_at__date': daily_sale['created_at__date'].strftime('%Y-%m-%d'),
            'daily_sales': daily_sale['daily_sales'],
        }
        daily_sales_list.append(daily_sale_dict)

    context = {
        'total_sales': total_sales,
        'category_sales': json.dumps(category_sales_list),
        'product_sales': product_sales,
        'daily_sales': json.dumps(daily_sales_list),
        'products' : products,
        'total_orders' : total_orders,
        'total_users' : total_users
        
    }
    return render(request, 'admin_dash.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class ViewPDF(View):
    def get(self, request, *args, **kwargs):

        orders = Order.objects.all()
        total_sales = Order.objects.filter(is_ordered=True).aggregate(total_sales=Sum('order_total'))['total_sales']

        category_sales = Category.objects.annotate(sales_revenue=Sum('product__orderproduct__product_price'))

        product_sales = Product.objects.annotate(sales_revenue=Sum('orderproduct__product_price'))

        start_date = date.today() - timedelta(days=7)
        daily_sales = Order.objects.filter(is_ordered=True, created_at__gte=start_date).values('created_at__date').annotate(daily_sales=Sum('order_total')).order_by('-created_at__date')

        previous_day_sales = Order.objects.filter(is_ordered=True, created_at__date=start_date - timedelta(days=1)).aggregate(previous_day_sales=Sum('order_total'))['previous_day_sales']
        increase_percentage = ((decimal.Decimal(total_sales) - decimal.Decimal(previous_day_sales)) / decimal.Decimal(previous_day_sales)) * 100 if previous_day_sales else 0

        context = {
            'total_sales': total_sales,
            'category_sales': category_sales,
            'product_sales': product_sales,
            'daily_sales': daily_sales,
            'increase_percentage': increase_percentage,
            'orders' : orders,
        }

        pdf = render_to_pdf('sales_report.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            return response
        return HttpResponse("Failed to generate PDF.")


class DownloadPDF(View):
   
    def get(self, request, *args, **kwargs):

        orders = Order.objects.all()
        total_sales = Order.objects.filter(is_ordered=True).aggregate(total_sales=Sum('order_total'))['total_sales']
        category_sales = Category.objects.annotate(sales_revenue=Sum('product__orderproduct__product_price'))
        product_sales = Product.objects.annotate(sales_revenue=Sum('orderproduct__product_price'))
        start_date = date.today() - timedelta(days=7)
        daily_sales = Order.objects.filter(is_ordered=True, created_at__gte=start_date).values('created_at__date').annotate(daily_sales=Sum('order_total')).order_by('-created_at__date')
        previous_day_sales = Order.objects.filter(is_ordered=True, created_at__date=start_date - timedelta(days=1)).aggregate(previous_day_sales=Sum('order_total'))['previous_day_sales']
        increase_percentage = ((decimal.Decimal(total_sales) - decimal.Decimal(previous_day_sales)) / decimal.Decimal(previous_day_sales)) * 100 if previous_day_sales else 0

        context = {
            'total_sales': total_sales,
            'category_sales': category_sales,
            'product_sales': product_sales,
            'daily_sales': daily_sales,
            'increase_percentage': increase_percentage,
            'orders' : orders,
        }

        pdf = render_to_pdf('sales_report.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename={}'.format(smart_str("sales_report.pdf"))
            response.write(pdf)
            return response
        return HttpResponse("Failed to generate PDF.")
    

@login_required(login_url = 'admin_login')
def user_manage(request):
    user = Account.objects.filter(is_admin = False)
    context = {
        'user' : user,
    }
    return render(request, 'user_manage.html', context)

    
def add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        user = Account(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
            phone_number = phone_number
        )
        user.save()
        return redirect('user_manage')

    return render(request, 'user_manage.html')
    

def update(request, id):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        user = Account(
            id = id,
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
            phone_number = phone_number
        )
        user.save()
        return redirect('user_manage')

    return render(request, 'user_manage.html')

def delete(request, id):
    user = Account.objects.filter(id=id)
    user.delete()
    return redirect('user_manage')

def change_status(request, id):
    if request.method == 'POST':
        user = Account.objects.get(id=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('user_manage')
    return render(request, 'user_manage.html')


@login_required(login_url = 'admin_login')
def admin_cat(request):
    category = Category.objects.all()
    context = {
        'category': category,
        'media_url': settings.MEDIA_URL,
    }
    return render(request, 'admin_cat.html', context)

def add_cat(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')

        category = Category(
        category_name = category_name,
        description = description,
        cat_image = cat_image
        )
        category.save()
        return redirect('admin_cat')
    
    return render(request, 'admin_cat.html')

    
def update_cat(request, id):

    category = Category.objects.get(id=id)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')

        category = Category(
            id = id,
            category_name = category_name,
            description = description,
            cat_image = cat_image
        )
        category.save()
        return redirect('admin_cat')
    
    return render(request, 'admin_cat.html')


def block_cat(request, id):
    category = get_object_or_404(Category, id=id)
    category.is_blocked = not category.is_blocked
    category.save()
    return redirect('admin_cat')

@login_required(login_url = 'admin_login')
def admin_product(request):
    category = Category.objects.all()
    product = Product.objects.all()
    context = {
        'product':product,
        'category':category
    }
    return render(request, 'admin_product.html', context)

def add_prod(request):
    
    if request.method == 'POST':
        print('add product')
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        images = request.FILES.get('images')
        is_available = request.POST.get('is_available')
        category = Category.objects.get(id=request.POST.get('category'))
        created_date = request.POST.get('created_date')
        modified_date = request.POST.get('modified_date')

        
        cropped_image_data = request.POST.get('cropped_image')
        cropped_image_data = cropped_image_data.split(',')[1] 
        cropped_image = base64.b64decode(cropped_image_data) 

        filename = f'{uuid.uuid4()}.jpg'
        file_path = os.path.join('media','photos','products',filename)

        try:
            with open(file_path, 'wb') as f:
                f.write(cropped_image)
        except Exception as e:
            print(f"Error saving the cropped image: {e}")

        access_path = file_path.replace('media' + os.sep, '', 1)


        product = Product(
            product_name = product_name,
            description = description,
            price = price,
            images=access_path,
            is_available = is_available,
            category = category,
            created_date = created_date,
            modified_date = modified_date
        )
        product.save()
        return redirect('admin_product')
    
    return render(request, 'admin_product.html')

def update_prod(request, id):

    product = Product.objects.get(id=id)
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_available = request.POST.get('is_available')
        category = Category.objects.get(id=request.POST.get('category'))
        created_date = request.POST.get('created_date')
        modified_date = request.POST.get('modified_date')

        images = request.FILES.get('images')

        if images:
            product.images = images

        product = Product(
            id=id,
            product_name = product_name,
            description = description,
            price = price,
            images = images,
            is_available = is_available,
            category = category,
            created_date = created_date,
            modified_date = modified_date
        )
        product.save()
       
        return redirect('admin_product')
    
    return render(request, 'admin_product.html')

def delete_prod(request, id):
    product = Product.objects.filter(id=id)
    product.delete()
    return redirect('admin_product')

@login_required(login_url = 'admin_login')
def admin_variation(request):
    product = Product.objects.all()
    variation = Variation.objects.all()
    context = {
        'product':product,
        'variation': variation
    }
    return render(request, 'admin_var.html', context)

def add_variation(request):

    if request.method == 'POST':
        product = Product.objects.get(id=request.POST.get('product'))
        variation_category = request.POST.get('variation_category')
        variation_value = request.POST.get('variation_value')
        stock = request.POST.get('stock')
        variant_image = request.FILES.get('variant_image')
        is_active = request.POST.get('is_active')
        created_date = request.POST.get('created_date')

        variation = Variation(
            product = product,
            variation_category = variation_category,
            variation_value = variation_value,
            variant_image = variant_image,
            stock = stock,
            is_active =is_active,
            created_date = created_date,
        )
        variation.save()
        return redirect('admin_variation')
    
    return render(request, 'admin_var.html')

def update_variation(request, id):

    variation = Variation.objects.get(id=id)

    if request.method == 'POST':
        product = Product.objects.get(id=request.POST.get('product'))
        variation_category = request.POST.get('variation_category')
        variation_value = request.POST.get('variation_value')
        variant_image = request.FILES.get('variant_image')
        stock = request.POST.get('stock')
        is_active = request.POST.get('is_active')
        created_date = request.POST.get('created_date')

        if variant_image:
            variation.variant_image = variant_image

        variation = Variation(
            id = id,
            product = product,
            variation_category = variation_category,
            variation_value = variation_value,
            variant_image = variant_image,
            stock = stock,
            is_active =is_active,
            created_date = created_date,
            )
        variation.save()
        return redirect('admin_variation')
    return render(request, 'admin_var.html')

def delete_variation(request, id):
    variation = Variation.objects.filter(id=id)
    variation.delete()
    return redirect('admin_variation')

@login_required(login_url = 'admin_login')
def admin_order(request):
    orders = Order.objects.prefetch_related('orderproduct_set').all()
    order_count = orders.count()
    paginator = Paginator(orders, 6)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
        'order_count' : order_count,

    }
    return render(request, 'admin_order.html', context)

def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
    return redirect('admin_order')


def cancel_order_admin(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'Cancelled'
        order.save()
    return redirect('admin_order')

def admin_order_detail(request, order_id):
    order_detail = OrderProduct. objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    sub_total = 0
    delivery_charge = order.delivery_charge
    discount = order.offer_discount+order.coupon_discount
    for i in order_detail:
        sub_total += i.product_price * i.quantity
    grand_total = sub_total + delivery_charge - discount
    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal': sub_total,
        'grand_total' : grand_total,
    }
    return render(request, 'admin_order_detail.html', context)

def search_order(request):
    query = request.GET['query']
    orders = Order.objects.filter(status__icontains=query)
    order_count = orders.count()
    paginator = Paginator(orders, 6)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
        'order_count' : order_count,

    }
    return render(request, 'admin_order.html', context)

def new_to_old(request):
    orders = Order.objects.all().order_by('-created_at')
    order_count = orders.count()
    paginator = Paginator(orders, 6)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
        'order_count' : order_count,

    }
    return render(request, 'admin_order.html', context)

def old_to_new(request):
    orders = Order.objects.all().order_by('created_at')
    order_count = orders.count()
    paginator = Paginator(orders, 6)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders,
        'order_count' : order_count,

    }
    return render(request, 'admin_order.html', context)

@login_required(login_url = 'admin_login')
def coupon_manage(request):
    coupons = Coupon.objects.all()
    return render(request, 'coupon_manage.html', {'coupons': coupons})

def create_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST['coupon_code']
        discount_price = request.POST['discount_price']
        is_expired = request.POST.get('is_expired', False)
        minimum_amount = request.POST['minimum_amount']
        
        coupon = Coupon.objects.create(coupon_code=coupon_code, discount_price=discount_price, is_expired=is_expired, minimum_amount=minimum_amount)

       
        return redirect('coupon_manage')
    
    return render(request, 'coupon_manage.html')

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    
    if request.method == 'POST':
        coupon_code = request.POST['coupon_code']
        discount_price = request.POST['discount_price']
        is_expired = request.POST.get('is_expired', False)
        minimum_amount = request.POST['minimum_amount']
        
        coupon.coupon_code = coupon_code
        coupon.discount_price = discount_price
        coupon.is_expired = is_expired
        coupon.minimum_amount = minimum_amount
        coupon.save()
        
        return redirect('coupon_manage')
    
    return render(request, 'coupon_manage.html')


def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.filter(id=coupon_id)
    coupon.delete()
    return redirect('coupon_manage')

@login_required(login_url = 'admin_login')
def cat_offer_manage(request):
    offers = CategoryOffer.objects.all()
    return render(request, 'cat_offer_manage.html', {'offers': offers})

def create_catoffer(request):

    if request.method == 'POST':

        description = request.POST['description']
        discount_percentage = request.POST['discount_percentage']
        is_expired = request.POST['is_expired']
        category = Category.objects.get(id=request.POST.get('category'))
       

        offer = CategoryOffer(
            description = description,
            discount_percentage = discount_percentage,
            is_expired = is_expired,
            category = category,
            )
        offer.save()

        return redirect('cat_offer_manage')
    
    return render(request, 'cat_offer_manage.html')

        
def edit_catoffer(request, id):

    offer = get_object_or_404(CategoryOffer, id=id)

    if request.method == 'POST':
        description = request.POST['description']
        discount_percentage = request.POST['discount_percentage']
        is_expired = request.POST['is_expired']
        category = Category.objects.get(id=request.POST.get('category'))

    
        offer.description = description
        offer.discount_percentage = discount_percentage
        offer.is_expired = is_expired
        offer.category = category
        offer.save()


        return redirect('cat_offer_manage')
    
    return render(request, 'cat_offer_manage.html', {'offer': offer})

def delete_catoffer(request, id):
    offers = CategoryOffer.objects.filter(id = id)
    offers.delete()
    return redirect('cat_offer_manage')

def min_offer_manage(request):
    offers = MinimumPurchaseOffer.objects.all()
    return render(request, 'min_offer_manage.html', {'offers': offers})

def create_minoffer(request):

    if request.method == 'POST':

        description = request.POST['description']
        discount_percentage = request.POST['discount_percentage']
        is_expired = request.POST['is_expired']
        minimum_purchase_amount = request.POST['minimum_purchase_amount']
       

        offer = MinimumPurchaseOffer(
            description = description,
            discount_percentage = discount_percentage,
            is_expired = is_expired,
            minimum_purchase_amount = minimum_purchase_amount,
            )
        offer.save()

        return redirect('min_offer_manage')
    
    return render(request, 'min_offer_manage.html')

        
def edit_minoffer(request, id):

    offer = get_object_or_404(MinimumPurchaseOffer, id=id)

    if request.method == 'POST':
        description = request.POST['description']
        discount_percentage = request.POST['discount_percentage']
        is_expired = request.POST['is_expired']
        minimum_purchase_amount = request.POST['minimum_purchase_amount']
    
        offer.description = description
        offer.discount_percentage = discount_percentage
        offer.is_expired = is_expired
        offer.minimum_purchase_amount = minimum_purchase_amount
        offer.save()


        return redirect('min_offer_manage')
    
    return render(request, 'min_offer_manage.html', {'offer': offer})

def delete_minoffer(request, id):
    offers = MinimumPurchaseOffer.objects.filter(id = id)
    offers.delete()
    return redirect('min_offer_manage')