from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

from .resumes.views import ResumeDetailView, ResumePDFView, ResumeListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^resume/(?P<username>[\w.@+-]+)/(?P<slug>[-\w]+)/(?P<object_id>\d+)/$',
        ResumeDetailView.as_view(), name='resume_detail'),
    url(r'^resume/(?P<username>[\w.@+-]+)/(?P<slug>[-\w]+)/(?P<object_id>\d+)/pdf/$',
        ResumePDFView.as_view(), name='resume_pdf'),
    url(r'^resumes/', ResumeListView.as_view(), name='resume_list'),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^panel/', include('panel.urls')),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if getattr(settings, 'SERVE_STATIC', False):
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
