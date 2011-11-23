from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin

from .cvm1.views import ResumeDetailView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<username>[\w.@+-]+)/(?P<slug>[-\w]+)/$',
        ResumeDetailView.as_view(), name='resume_detail'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
