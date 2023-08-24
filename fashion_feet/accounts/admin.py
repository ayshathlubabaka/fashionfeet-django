from django.contrib import admin
from .models import Account, UserProfile, Wallet, Referral, ReferralCode, Transaction

admin.site.register(Account)
admin.site.register(UserProfile)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Referral)
admin.site.register(ReferralCode)