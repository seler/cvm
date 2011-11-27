from __future__ import absolute_import
from django.conf.urls.defaults import patterns, url, include
from .views import home, IdentityUpdateView, IdentityCreateView, ShareCreateView, ShareUpdateView

urlpatterns = patterns('',
    url(r'^$', home, name='panel_home'),
    url(r'^identity/create/$', IdentityCreateView.as_view(), name='panel_identity_create'),
    url(r'^identity/(?P<pk>[0-9]+)/$', IdentityUpdateView.as_view(), name='panel_identity_update'),
    url(r'^identity/delete/(?P<pk>[0-9]+)/$', IdentityUpdateView.as_view(), name='panel_identity_delete'),
    url(r'^resume/create/$', IdentityCreateView.as_view(), name='panel_resume_create'),
    url(r'^resume/(?P<pk>[0-9]+)/$', IdentityUpdateView.as_view(), name='panel_resume_update'),
    url(r'^resume/delete/(?P<pk>[0-9]+)/$', IdentityUpdateView.as_view(), name='panel_resume_delete'),
    url(r'^resume/share/(?P<resume_pk>[0-9]+)/$', ShareCreateView.as_view(), name='panel_resume_share'),
    url(r'^share/create/$', ShareCreateView.as_view(), name='panel_share_create'),
    url(r'^share/(?P<pk>[0-9]+)/$', ShareUpdateView.as_view(), name='panel_share_update'),
    url(r'^share/delete/(?P<pk>[0-9]+)/$', IdentityUpdateView.as_view(), name='panel_share_delete'),
)
