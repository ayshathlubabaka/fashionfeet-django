from django import forms
from .models import Account, UserProfile

class Registrationform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password'
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'password']

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name','phone_number')  

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')