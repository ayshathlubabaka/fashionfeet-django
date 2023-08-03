from . import views
from django.urls import path
from .views import send_otp, verify_otp, signup, login, user_logout
   
urlpatterns = [
    path('send-otp/<str:phone_number>/', send_otp, name='send_otp'),
    path('verify-otp/<str:phone_number>/', verify_otp, name='verify_otp'),
    path('signup/', signup, name='signup'),
    path('', login, name='login'),
    path('user_logout/', user_logout, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password')
]