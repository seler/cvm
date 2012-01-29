from django.conf.urls.defaults import patterns

urlpatterns = patterns('cms.views',
    (r'^(?P<url>.*)$', 'page'),
)
