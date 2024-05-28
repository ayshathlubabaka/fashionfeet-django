from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account, ReferralCode
import shortuuid

@receiver(post_save, sender=Account)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        referral_code = ReferralCode.objects.create(user=instance)
        referral_code.code = shortuuid.uuid()[:8]  
        referral_code.save()