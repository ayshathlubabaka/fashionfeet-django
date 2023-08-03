from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Product, Category

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
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def men_product_list(request):
    products = Product.objects.filter(category__category_name = 'Men')
    return render(request, 'product_list.html', {'products': products})

def women_product_list(request):
    products = Product.objects.filter(category__category_name = 'Women')
    return render(request, 'product_list.html', {'products': products})

def view_prod(request, id):
    product = get_object_or_404(Product, id=id)

    # Pass the product data to the template
    context = {
        'product': [product]
    }
    return render(request, 'view_prod.html', context)