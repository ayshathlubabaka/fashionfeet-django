from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('Men/', views.men_product_list, name='men_product_list'),
    path('product_list/', views.product_list, name='product_list'),
    path('Women/', views.women_product_list, name='women_product_list'),
    path('view_prod/<str:id>/', views.view_prod, name='view_prod'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)