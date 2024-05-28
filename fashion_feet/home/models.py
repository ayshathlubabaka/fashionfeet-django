from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import Permission
from accounts.models import Account
from django.db.models import Avg
from cloudinary.models import CloudinaryField
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    # cat_image = models.ImageField(upload_to='photos/products', blank= True)
    cat_image = CloudinaryField('cat_image')

    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name
    

class Product(models.Model):
    product_name = models.CharField(max_length= 100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    price = models.IntegerField()
    new_price = models.IntegerField(null=True, default=0)
    # images = models.ImageField(upload_to='photos/products')
    images = CloudinaryField('images')
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    
variation_category_choice = (
    ('color','color'),
    ('size','size'),
)
    

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    # variant_image = models.ImageField(upload_to='photos/products', blank=True)
    variant_image = CloudinaryField('variant_image')
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class WishlistItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name}'s Wishlist: {self.product.product_name}"
    

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=0)
    minimum_amount = models.IntegerField(default=1000)


class CategoryOffer(models.Model):
    description = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} Offer"
    
class MinimumPurchaseOffer(models.Model):
    description = models.CharField(max_length=100)
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.FloatField()
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"Minimum Purchase Offer"
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
