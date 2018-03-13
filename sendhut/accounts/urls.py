from django.conf.urls import url
from .views import (
    ProfileView, PasswordResetView, PasswordResetConfirmView,
    change_password
)


urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    # password reset
    url(r'^reset-password/$', PasswordResetView.as_view(),
        name='password_reset'),
    url(r'^reset/(?P<token>[0-9A-Za-z]{1,13})/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^password/$', change_password, name='change_password'),
]
