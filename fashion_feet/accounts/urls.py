from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('add_profile/', views.add_profile, name='add_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('change_password/', views.change_password, name="change_password"),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel_order/<int:order_id>', views.cancel_order, name='cancel_order'),
    path('referral/<str:code>/', views.referral_link, name='referral_link'),
    path('wallet/', views.wallet, name='wallet'),
    path('add_money_to_wallet/', views.add_money_to_wallet, name='add_money_to_wallet'),
]