from django.contrib.auth import authenticate, login, logout

from django.views import View
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings

from sendhut.cart import Cart
from sendhut import utils
from sendhut.accounts.models import User
from .forms import LoginForm, SignupForm, ProfileForm


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
    # TODO(yao): password reset

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
            user = authenticate(request, username=username, password=password)
            if user:
                cart_data = Cart(request).serialize_lite()
                login(request, user)
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
                # restore cart from anonymous user sesssion
                Cart(request, cart_data)
                return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'accounts/login.html', {
            'login_form': LoginForm(),
            'signup_form': signup_form
        })
