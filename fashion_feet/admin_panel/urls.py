from . import views
from django.urls import path


urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('admin_dash/', views.admin_dash, name='admin_dash'),
    path('admin_product/', views.admin_product, name='admin_product'),
    path('user_manage/', views.user_manage, name='user_manage'),
    path('add_user', views.add_user, name ='add_user'),
    path('update/<str:id>', views.update, name='update'),
    path('delete/<str:id>', views.delete, name='delete'),
    path('change_status/<str:id>', views.change_status, name='change_status'),
    path('admin_cat/', views.admin_cat, name='admin_cat'),
    path('add_cat', views.add_cat, name='add_cat'),
    path('update_cat/<str:id>', views.update_cat, name='update_cat'),
    path('add_prod', views.add_prod, name='add_prod'),
    path('update_prod/<str:id>', views.update_prod, name='update_prod'),
    path('delete_prod/<str:id>', views.delete_prod, name='delete_prod'),
    path('admin_variation/', views.admin_variation, name='admin_variation'),
     path('add_variation', views.add_variation, name='add_variation'),
    path('update_variation/<str:id>', views.update_variation, name='update_variation'),
    path('delete_variation/<str:id>', views.delete_variation, name='delete_variation'),

]
