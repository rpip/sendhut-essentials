from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect, render
from django.conf import settings

from .cart import Cart
from .forms import LoginForm


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Home'
        return context


class AboutPageView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About'
        return context


class ProfileView(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                cart_data = Cart(request).serialize_lite()
                login(request, user)
                # restore cart from anonymous user sesssion
                Cart(request, cart_data)
                return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        cart_data = Cart(request).serialize_lite()
        logout(request)
        # restore cart from anonymous user sesssion
        Cart(request, cart_data)
        return redirect(settings.LOGIN_REDIRECT_URL)
