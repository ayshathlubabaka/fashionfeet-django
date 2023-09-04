from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from orders.models import OrderProduct
from .models import Product, Category, WishlistItem, CategoryOffer, Variation, ReviewRating
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F
from django.http import JsonResponse
from .forms import ReviewForm
from django.contrib import messages
# Create your views here.

def home(request):
    products = Product.objects.all()
    category = Category.objects.all()
    context = {
        'products' : products,
        'category':category
    }
    return render(request, 'index.html', context)

def sort_products(products, sort_by):
    if sort_by == 'newToOld':
        sorted_products = sorted(products, key=lambda p: p.created_date, reverse=True)
    elif sort_by == 'oldToNew':
        sorted_products = sorted(products, key=lambda p: p.created_date)
    elif sort_by == 'highToLow':
        sorted_products = sorted(products, key=lambda p: p.price, reverse=True)
    elif sort_by == 'lowToHigh':
        sorted_products = sorted(products, key=lambda p: p.price)
    else:
        sorted_products = products

    return sorted_products


def product_list(request, id=None):

    all_products = Product.objects.all()
    for i in all_products:
        i.new_price = i.price
        i.save()

    try:
        category_offer = CategoryOffer.objects.get(id=1)
        discount_percentage = category_offer.discount_percentage
        offer_products = Product.objects.filter(category=category_offer.category)
    except CategoryOffer.DoesNotExist:
        category_offer = None
        discount_percentage = 0
        offer_products = []
    
    if id is not None:
        products = Product.objects.all().filter(category__id = id,is_available=True, category__is_blocked=False).order_by('product_name')
    else:
        products = Product.objects.all().filter(is_available=True, category__is_blocked=False).order_by('product_name')

    variations = Variation.objects.filter(stock__lte=0)
    for variation in variations:
        variation.is_active = False
        variation.save()

    all_inactive = True
    for variation in Variation.objects.all():
        if variation.is_active:
            all_inactive = False
            break

    
    for p in products:
        for i in offer_products:
            if p==i:
                p.new_price = p.price- (discount_percentage*p.price/100)
                p.save()

    product_count = products.count()
    sort_by = request.GET.get('sort')
    products = sort_products(products, sort_by)
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
        'products' : paged_products,
        'product_count' : product_count,
        'sort': sort_by,
        'offer_products' : offer_products,
        'discount_percentage' : discount_percentage,
        'all_inactive' : all_inactive
    }
    return render(request, 'product_list.html', context)

def view_prod(request, id):
    product = get_object_or_404(Product, id=id)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user = request.user, product_id = product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'product': [product],
        'in_cart' : in_cart,
        'orderproduct' : orderproduct,
        'reviews' : reviews,
    }
    return render(request, 'view_prod.html', context)

def autocomplete(request):
    keyword = request.GET.get('keyword')
    if keyword:
        products = Product.objects.filter(product_name__icontains=keyword).values_list('product_name', flat=True)
        return JsonResponse(list(products), safe=False)
    return JsonResponse([], safe=False)

def search(request):
    keyword = request.GET.get('keyword', '')  

    if keyword:
        products = Product.objects.order_by('-created_date').filter(product_name__icontains=keyword)
        
    else:
        products = []  

    context = {
        'products': products,
    }
    return render(request, 'product_list.html', context)

def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        WishlistItem.objects.create(product=product, user=request.user)
    return redirect('wishlist')

def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')

def wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
    else:
        wishlist_items = None 
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thankyou! Your review is updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thankyou! Your review has been submitted')
                return redirect(url)
