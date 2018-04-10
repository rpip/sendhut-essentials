from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from sendhut.accounts.views import LoginView, LogoutView, SignupView
from sendhut.lunch.views import PartnerSignupView
from sendhut.grouporder.views import CartJoin

from .views import home, about, faqs, privacy_terms


urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^about-us/$', about, name='about-us'),
    url(r'^faqs/$', faqs, name='faqs'),
    url(r'^privacy_terms/$', privacy_terms, name='privacy-terms'),
    url(r'^partner/$', PartnerSignupView.as_view(), name='partner-signup'),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^login/$', LoginView.as_view(), name='signin'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/', include('sendhut.accounts.urls', namespace='accounts')),
    url(r'^lunch/', include('sendhut.lunch.urls', namespace='lunch')),
    url(r'^group/', include('sendhut.grouporder.urls', namespace='group')),
    url(r'^cart/(?P<ref>[a-zA-Z0-9-]+)$', CartJoin.as_view(), name='join-group-order'),
    url(r'^checkout/', include('sendhut.checkout.urls', namespace='checkout')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include('loginas.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
