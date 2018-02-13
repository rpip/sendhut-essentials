from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, SetPasswordForm
from .models import User


class PasswordResetForm(forms.Form):
    phone = forms.CharField(
        label='Mobile Phone',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}))


class PasswordResetConfirmForm(SetPasswordForm):
    phone = forms.CharField(
        label='Mobile Phone',
        max_length=20,
        required=False,
        widget=forms.HiddenInput())


class LoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        label='Your Email or Mobile number',
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    remember_me = forms.BooleanField(required=False, widget=forms.HiddenInput())


class SignupForm(forms.Form):
    first_name = forms.CharField(
        label='First name',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
    last_name = forms.CharField(
        label='Last name',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
    phone = forms.CharField(
        label='Mobile Phone',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Your mobile phone number'}))
    password = forms.CharField(
        label='Password',
        max_length=20,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    email = forms.EmailField(
         label='Email',
         max_length=30,
         widget=forms.TextInput(attrs={'placeholder': 'e.g. name@example.com'}))


class ProfileForm(forms.ModelForm):
    # TODO(yao): add notification toggles
    # TODO(yao): add address form
    # TODO(yao): confirm new email

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')
