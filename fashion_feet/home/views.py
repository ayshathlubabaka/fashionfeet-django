from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Product, Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.

def home(request):
    products = Product.objects.all()
    category = Category.objects.all()
    context = {
        'products' : products,
        'category':category
    }
    return render(request, 'index.html', context)


def product_list(request):
    products = Product.objects.all().filter(is_available=True).order_by('product_name')
    product_count = products.count()
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products' : paged_products,
        'product_count' : product_count
    }
    return render(request, 'product_list.html', context)


def men_product_list(request):
    products = Product.objects.filter(category__category_name = 'Men', is_available=True)
    product_count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products' : paged_products,
        'product_count' : product_count
    }
    return render(request, 'product_list.html', context)

def women_product_list(request):
    products = Product.objects.filter(category__category_name = 'Women',is_available=True)
    product_count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products' : paged_products,
        'product_count' : product_count
    }
    return render(request, 'product_list.html', context)

def view_prod(request, id):
    product = get_object_or_404(Product, id=id)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()


    # Pass the product data to the template
    context = {
        'product': [product],
        'in_cart' : in_cart
    }
    return render(request, 'view_prod.html', context)