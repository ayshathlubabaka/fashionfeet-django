from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account
from home.models import Category, Product, Variation
from django.contrib.auth.models import auth
from django.contrib import messages

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
            print('invalid credentials')
            messages.info(request, 'invalid credentials')
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')


def admin_dash(request):
    return render(request, 'admin_dash.html')

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
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        images = request.FILES.get('images')
        is_available = request.POST.get('is_available')
        category = Category.objects.get(id=request.POST.get('category'))
        created_date = request.POST.get('created_date')
        modified_date = request.POST.get('modified_date')

        product = Product(
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




