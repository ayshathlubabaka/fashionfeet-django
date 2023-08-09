from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id
from .forms import UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib.auth import authenticate, login as user_login, logout
import requests
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



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
        
        current_site = get_current_site(request)
        mail_subject = 'Please activate your account'
        message = render_to_string('account_verification_email.html',{
            'user' : user,
            'domain' : current_site,
            'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
            'token' : default_token_generator.make_token(user),
        })
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        messages.success(request, 'Thankyou for registering with us. We have sent a verification email. Please try it')
        
        return redirect('register')
     
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
    
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations ! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_password_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset has been sent to you email address')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist')  
            return redirect('forgotPassword')  
    return render(request, 'forgotPassword.html')

def resetpassword_validate(request, uidb64, token ):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password1']
        confirm_password = request.POST['password2'] 

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.success(request, 'Password do not match')
            return redirect('resetPassword')
    else:
        return render(request, 'resetPassword.html')
    
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
       user_form = UserForm(request.POST, instance=request.user)
       profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
       
       if user_form.is_valid() and profile_form.is_valid():
           user_form.save()
           profile_form.save()
           messages.success(request, 'Your profile has been updated')
           return redirect('edit_profile')
    else:
           user_form = UserForm(instance=request.user)
           profile_form = UserProfileForm(instance=userprofile)
    context = {
           'user_form' : user_form,
           'profile_form' : profile_form,
    }

    return render(request, 'edit_profile.html', context)