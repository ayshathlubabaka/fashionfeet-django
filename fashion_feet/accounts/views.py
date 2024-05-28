from datetime import timezone
import datetime
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id
from orders.models import OrderProduct
from .forms import UserForm, UserProfileForm, Registrationform
from .models import Account, UserProfile, ReferralCode, Referral, Wallet, Transaction
from django.contrib.auth import authenticate, login as user_login, logout
import requests
from django.contrib import messages
from orders.models import Order
from django.http import JsonResponse
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
        referral_code = request.POST.get('referral_code')
        
        
        if password != confirm_password:
            error_message = "Passwords do not match"
            return render(request, 'register.html', {'error_message': error_message})
        
        if Account.objects.filter(email=email).exists():
            error_message = "Email already exists"
            return render(request, 'register.html', {'error_message': error_message})
        
        
        if Account.objects.filter(username=username).exists():
            error_message = "Username already exists"
            return render(request, 'register.html', {'error_message': error_message})
        
        
        
        user = Account.objects.create_user(username=username,first_name=first_name, last_name=last_name, email=email, password=password)
        user.phone_number = phone_number
        user.save()

        wallet = Wallet.objects.create(user=user, balance=0.00)
        wallet.save()
        
        if referral_code:
            try:
                referrer_code = ReferralCode.objects.get(code=referral_code, status=True)
                referrer = referrer_code.user
                referral = Referral(referrer=referrer, referred_user=user)
                referral.save()

                wallet = Wallet.objects.get(user = referrer)
                wallet.add_funds(25)
                wallet.save()

                wallet = Wallet.objects.get(user=user)
                wallet.add_funds(25)
                wallet.save()
                
            except ReferralCode.DoesNotExist:
                pass

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
                
                params = dict(x.split('=')for x in query.split('&'))
                
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
               
            except:
                 return redirect('home')
        else:
            messages.error(request, 'Please enter valid credentials')
            return render(request, 'login.html')
    
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

@login_required(login_url='login')  
def edit_profile(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=request.user)
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

    try:
        referral_code = request.user.referralcode
        code = referral_code.code
    except:
        code = None
    context = {
           'user_form' : user_form,
           'profile_form' : profile_form,
           'userprofile' : userprofile,
           'code' : code,
    }


    return render(request, 'edit_profile.html', context)

@login_required(login_url='/login')
def my_orders(request):

    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders' : orders,
    }   
    return render(request, 'my_orders.html', context)

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order.status = 'Cancelled'
        order.save()
        try:
            wallet = Wallet.objects.get(user=request.user)
            amount = Decimal(order.order_total)
            wallet.add_funds(amount)
        except Wallet.DoesNotExist:
            pass
    return redirect('my_orders')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect ('change_password')
            else:
                messages.error(request, 'Please enter valid password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match')
            return redirect('change_password')
    return render(request, 'change_password.html')

def order_detail(request, order_id):
    order_detail = OrderProduct. objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    sub_total = 0
    delivery_charge = order.delivery_charge
    discount = order.offer_discount+order.coupon_discount
    for i in order_detail:
        sub_total += i.product_price * i.quantity
    grand_total = sub_total + delivery_charge - discount
    print(grand_total)
    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal': sub_total,
        'grand_total' : grand_total
    }
    return render(request, 'order_detail.html', context)

@login_required
def add_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Profile created successfully')
            return redirect('edit_profile')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'edit_profile.html', context)

def wallet(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
        balance = wallet.balance
        transaction = Transaction.objects.filter(wallet = wallet, timestamp__gte=datetime.datetime.now() - datetime.timedelta(days=7)).order_by('-timestamp')

        context = {
            'balance': balance,
            'transaction' : transaction
        }
        
        return render(request, 'wallet.html', context)
    except Wallet.DoesNotExist:
        return render(request, 'wallet.html')

def add_money_to_wallet(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        amount = Decimal(amount)
        wallet = Wallet.objects.get(user=request.user)
        wallet.add_funds(amount)
        wallet.save()
    return redirect('wallet')

@login_required
def assign_referral_code(request):
    if request.method == 'POST':
        referral_code = request.POST.get('referral_code')
        user = request.user

        try:
            code = ReferralCode.objects.get(code=referral_code, status=True)
            code.user = user
            code.save()
            return render(request, 'success.html')
        except ReferralCode.DoesNotExist:
            return render(request, 'invalid_code.html')

    return render(request, 'assign_referral_code.html')

def referral_link(request, code):
    try:
        referal_code = ReferralCode.objects.get(user = request.user)
        code = referal_code.code
        return render(request, 'referral_link.html', {'code': code})
    except:
        pass
   