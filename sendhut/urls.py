from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from sendhut.lunch import urls as lunch_urls
from sendhut.accounts import urls as account_urls
from sendhut.dashboard import urls as dashboard_urls
from .views import (
    HomePageView, AboutPageView,
    LoginView, LogoutView
)

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^about/$', AboutPageView.as_view(), name='about'),
    url(r'^accounts/', include(account_urls, namespace='accounts')),
    url(r'^lunch/', include(lunch_urls, namespace='lunch')),
    url(r'^business/', include(dashboard_urls, namespace='dashboard')),
    url(r'^admin/', include(admin.site.urls)),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
