from django.conf.urls import patterns, include, url
import gextracto
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
					   url(r'^', include('gextracto.urls', namespace="oauth2")),
					   # url(r'^blog/', include('blog.urls')),
					   url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
					   url(r'^admin/', include(admin.site.urls)),
					  ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
