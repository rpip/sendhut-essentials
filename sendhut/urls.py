from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin

from sendhut import lunch


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"),
        name='about'),
    url(r'^lunch/', include(lunch.urls, namespace='lunch')),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
