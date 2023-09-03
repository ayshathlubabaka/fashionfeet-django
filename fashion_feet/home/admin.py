from django.contrib import admin
from .models import Category,Product, Variation, Coupon, CategoryOffer, MinimumPurchaseOffer, WishlistItem, ReviewRating
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Variation)
admin.site.register(Coupon)
admin.site.register(CategoryOffer)
admin.site.register(MinimumPurchaseOffer)
admin.site.register(WishlistItem)
admin.site.register(ReviewRating)