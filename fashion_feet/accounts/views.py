from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id
from .forms import Registrationform
from .models import Account
from django.contrib.auth import authenticate, login as user_login, logout
import requests

def register(request):
     if request.method == 'POST':
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = email.split("@")[0]
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        
        if password != confirm_password:
            error_message = "Passwords do not match"
            return render(request, 'register.html', {'error_message': error_message})
        
        
        user = Account.objects.create_user(username=username,first_name=first_name, last_name=last_name, email=email, password=password)
        user.phone_number = phone_number
        user.save()
        
        
        return redirect('login')
     
     return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:

            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)

                    ex_var_list=[]
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
           
            user_login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print('query=',query)
                params = dict(x.split('=')for x in query.split('&'))
                print(params)
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
               
            except:
                 return redirect('home')
        else:
            error_message = "Invalid email or password"
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html')

@login_required(login_url = 'login')
def user_logout(request):
    logout(request)
    return redirect('home')
    
