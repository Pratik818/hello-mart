from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your full shipping address'}),
        label='Shipping Address'
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
        label='Phone Number'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special instructions? (optional)'}),
        label='Order Notes'
    )
