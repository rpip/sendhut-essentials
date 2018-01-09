from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from sendhut.lunch import urls as lunch_urls
from sendhut.accounts import urls as account_urls
from sendhut.dashboard import urls as dashboard_urls
from sendhut.accounts.views import LoginView, LogoutView, SignupView
from .views import (
    home, about, faqs, privacy_terms
)

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^about-us/$', about, name='about-us'),
    url(r'^faqs/$', faqs, name='faqs'),
    url(r'^privacy_terms/$', privacy_terms, name='privacy-terms'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/', include(account_urls, namespace='accounts')),
    url(r'^lunch/', include(lunch_urls, namespace='lunch')),
    url(r'^business/', include(dashboard_urls, namespace='dashboard')),
    url(r'^admin/', include(admin.site.urls)),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
