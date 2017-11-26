from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin

from sendhut.lunch import urls as lunch_urls
from .views import HomePageView, AboutPageView

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^about/$', AboutPageView.as_view(), name='about'),
    url(r'^lunch/', include(lunch_urls, namespace='lunch')),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
