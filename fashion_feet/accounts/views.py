from django.contrib.auth import login as user_login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from twilio.rest import Client
from .models import User
import random
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import auth

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(request, phone_number):
    
    otp = generate_otp()  
    
    user = User.objects.get(phone_number=phone_number)
    user.otp = otp
    user.save()
       
    account_sid = 'ACda783bac9580f38f8b81353cf2277968'
    auth_token = 'fc66edc5dcb4f68d7871ec681785f75f'
    client = Client(account_sid, auth_token)
       
    message = client.messages.create(
        body=f'Your OTP is: {otp}',
        from_='+14706192284',
        to=phone_number
    )
       
    return redirect('verify_otp', phone_number=phone_number)

def verify_otp(request, phone_number):
    if request.method == 'POST':
        otp_entered = request.POST['otp']
           
        user = User.objects.get(phone_number=phone_number)
           
        if otp_entered == user.otp:
            
            user.is_phone_verified = True
            user.save()
               
            user_login(request, user)
               
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verify_otp', phone_number=phone_number)
    else:
        return render(request, 'verify_otp.html', {'phone_number': phone_number})
    

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered')
            return redirect('signup')
        
        user = User.objects.create_user(phone_number=phone_number, username=username ,email=email, password=password)
        user.save()
        
        return send_otp(request, phone_number)
    else:
        return render(request, 'signup.html')
    
def login(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        user = auth.authenticate(phone_number=phone_number, password=password)

        if user and user.is_active:
            user_login(request, user)
            return redirect('home')
        else:
            print('invalid credentials')
            messages.info(request, 'invalid credentials')
            return redirect('login')
    
    return render(request, 'login.html')

def forgot_password(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user = User.objects.get(phone_number=phone_number)

        if user and user.is_active:
            return send_otp(request, phone_number)
        else:
            messages.error(request, 'Phone Number is not valid')
            return redirect('login')
    else:
        return render(request, 'forgot_password.html')
def user_logout(request):
    logout(request)
    return redirect('/')