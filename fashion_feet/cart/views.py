from django.shortcuts import get_object_or_404, render, redirect
from home.models import Variation, Product, MinimumPurchaseOffer, CategoryOffer
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import UserProfile
# Create your views here.


def _cart_id(request):
    
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):

    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []

        
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    
                
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list=[]
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            for i, variation_list in enumerate(ex_var_list):
                if set(product_variation) == set(variation_list):
                    item_id = id[i]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    for variation in product_variation:
                        
                        if variation.stock < item.quantity:
                            response_data = {
                                'error': 'Some variations are out of stock.',
                            }
                            return JsonResponse(response_data)
                    item.save()
                    quantity = item.quantity
                    sub_total = item.product.price * quantity
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        response_data = {
                            'quantity': quantity,
                            'sub_total': sub_total,
                        }
                        return JsonResponse(response_data)
                    break
        
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.set(product_variation)
                item.save()
                quantity = item.quantity
                sub_total = item.product.price * quantity
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    response_data = {
                        'quantity': quantity,
                        'sub_total': sub_total,
                    }
                    return JsonResponse(response_data)
                
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')
    
    else:
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list=[]
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                for variation in product_variation:
                    if variation.stock < item.quantity:
                        response_data = {
                            'error': 'Some variations are out of stock.',
                        }
                        return JsonResponse(response_data)
                item.save()
                quantity = item.quantity
                sub_total = item.product.price * quantity
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    response_data = {
                        'quantity': quantity,
                        'sub_total': sub_total,
                    }
                    return JsonResponse(response_data)
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                quantity = item.quantity
                sub_total = item.product.price * quantity
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    response_data = {
                        'quantity': quantity,
                        'sub_total': sub_total,
                    }
                    return JsonResponse(response_data)
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart=cart,
            )

            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save() 

        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()
            quantity = cart_item.quantity
            sub_total = cart_item.product.price * quantity
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'quantity': quantity,
                    'sub_total': sub_total,
                }
                return JsonResponse(response_data)
        else:
            cart_item.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'quantity': 0,  # Indicate that the cart item is removed
                    'sub_total': 0,  # Indicate that the cart item is removed
                }
                return JsonResponse(response_data)
    except:
        pass
    
    
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    print('cart_item_id',cart_item_id)
    cart_item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {
            'message': 'Cart item removed successfully.',
        }
        return JsonResponse(response_data)
    
    return redirect('cart')



def cart(request, total=0, delivery_charge=0,cart_items=None):
    
    try:
        quantity=0
        grand_total = 0
        discount_price = 0
        discount=0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            discount_price += (cart_item.product.new_price * cart_item.quantity)

        discount = total - discount_price
        delivery_charge = 30
        grand_total = total + delivery_charge - discount

    except ObjectDoesNotExist:
        pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {
        'total' : total,
        'delivery_charge' : delivery_charge,
        'grand_total':grand_total,
        'discount' : discount,
        }
        return JsonResponse(response_data)

    context = {
        'cart_items' : cart_items,
        'quantity' : quantity,
        'total' : total,
        'delivery_charge' : delivery_charge,
        'grand_total':grand_total,
        'discount' : discount,

    }
    
    return render(request, 'cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, delivery_charge = 0, grand_total = 0, cart_items=None):

    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.address_line_1:
            print('full adrees')
        else:
            print('no full_address')
    except UserProfile.DoesNotExist:
        user_profile = None
    try:
        cat_offer = CategoryOffer.objects.first()
    except CategoryOffer.DoesNotExist:
        cat_offer = None 

    try:
        min_offer = MinimumPurchaseOffer.objects.first()
    except MinimumPurchaseOffer.DoesNotExist:
        min_offer = None  

    if min_offer:
        min_discount_per = min_offer.discount_percentage
    else:
        min_discount_per = 0
    discount_price = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            if cart_item.product.new_price is not None and cart_item.product.new_price > 0:
                discount_price += (cart_item.product.new_price * cart_item.quantity)
            else:
                discount_price += (cart_item.product.price * cart_item.quantity) 
            quantity += cart_item.quantity
            cat_discount = total - discount_price
        min_discount = (total*min_discount_per/100)
        delivery_charge = 30
        grand_total = total + delivery_charge-cat_discount

    except ObjectDoesNotExist:
        pass
    context = {
        'min_offer' : min_offer,
        'cat_offer' : cat_offer,
        'cart_items' : cart_items,
        'quantity' : quantity,
        'total' : total,
        'delivery_charge' : delivery_charge,
        'grand_total':grand_total,
        'min_discount' : min_discount,
        'cat_discount' : cat_discount,
        'user_profile' : user_profile

    }
    return render(request, 'checkout.html', context)