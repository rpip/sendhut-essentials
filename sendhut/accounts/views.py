import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.views import View
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings

from sendhut.cart import Cart
from sendhut import utils, notifications
from sendhut.accounts.models import User
from .forms import (
    LoginForm, SignupForm, ProfileForm, PasswordResetForm,
    PasswordResetConfirmForm
)


logger = logging.getLogger(__file__)


class ProfileView(View):
    # TODO(yao): CRUD delivery addresses

    def get(self, request, *args, **kwargs):
        form = ProfileForm(instance=request.user)
        context = {'form': form}
        return render(request, 'accounts/profile.html', context)

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('accounts:profile')
        else:
            context = {'form': form}
            return render(request, 'accounts/profile.html', context)


class LoginView(View):

    def get(self, request, *args, **kwargs):
        login_form = LoginForm()
        signup_form = SignupForm()
        return render(request, 'accounts/login.html', {
            'login_form': login_form,
            'signup_form': signup_form
        })

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(data=request.POST)
        signup_form = SignupForm()
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            remember_me = login_form.cleaned_data['remember_me']
            user = authenticate(request, username=username, password=password)
            if user:
                cart_data = Cart(request).serialize_lite()
                login(request, user)
                if not remember_me:
                    self.request.session.set_expiry(0)
                # restore cart from anonymous user sesssion
                Cart(request, cart_data)
                next_url = request.GET.get('next') or settings.LOGIN_REDIRECT_URL
                return redirect(next_url)

        return render(request, 'accounts/login.html', {
            'login_form': login_form,
            'signup_form': signup_form
        })


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        cart_data = Cart(request).serialize_lite()
        logout(request)
        # restore cart from anonymous user sesssion
        Cart(request, cart_data)
        return redirect(settings.LOGIN_REDIRECT_URL)


class SignupView(LoginView):

    def post(self, request, *args, **kwargs):
        # TODO(yao): verify email
        signup_form = SignupForm(data=request.POST)
        if signup_form.is_valid():
            user = User(**signup_form.cleaned_data)
            user.username = utils.generate_random_name()
            user.save()
            if user:
                cart_data = Cart(request).serialize_lite()
                login(request, user)
                notifications.send_welcome_email(user.email)
                # restore cart from anonymous user sesssion
                Cart(request, cart_data)
                return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'accounts/login.html', {
            'login_form': LoginForm(),
            'signup_form': signup_form
        })


class PasswordResetView(View):

    def get(self, request):
        template = 'registration/password_reset_form.html'
        return render(request, template, {'form': PasswordResetForm()})

    def post(self, request):
        form = PasswordResetForm(data=request.POST)
        template = 'registration/password_reset_done.html'
        if form.is_valid():
            email = form.cleaned_data['email']
            token = utils.generate_password_token(email)
            notifications.send_password_reset(email, token)

        # if email doesn't exist, just ignore
        return render(request, template)


class PasswordResetConfirmView(View):

    def get(self, request, *args, **kwargs):
        template = 'registration/password_reset_confirm.html'
        token = kwargs['token']
        email = utils.check_password_token(token)
        user = User.objects.get(email=email) if email else None
        logger.warn("%s %s", user, email)
        from remote_pdb import set_trace
        set_trace()
        validlink = bool(user)
        context = {
            'form': PasswordResetConfirmForm(user=user, data={'email': email}),
            'validlink': validlink
        }
        return render(self.request, template, context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.POST.get('email').strip())
        form = PasswordResetConfirmForm(user=user, data=request.POST)
        template = 'registration/password_reset_confirm.html'
        if form.is_valid():
            form.save()
            messages.info(request, "Your password has been changed. Login to continue")
            return redirect('signin')

        return render(
            self.request, template,
            {'form': form, 'validlink': True})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
