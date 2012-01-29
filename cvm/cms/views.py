from cms.models import Page
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.db.models.base import get_absolute_url
from django.utils import translation
from datetime import datetime
from django.db.models.query import QuerySet

DEFAULT_TEMPLATE = 'pages/default.html'

def page(request, url):
    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)
    if not url.startswith('/'):
        url = "/" + url


    if 'lang' not in request.COOKIES:
        translation.activate(translation.get_language_from_request(request))
    if 'lang' in request.GET:
        if translation.check_for_language(request.GET['lang']):
            translation.activate(request.GET['lang'])

    pages = Page.objects.filter(sites__id__exact=settings.SITE_ID)
    for p in pages:
        if url != p.get_absolute_url():
            pages = pages.exclude(pk=p.pk)

    if not request.user.is_authenticated():
        pages = pages.filter(registration_required=False)
    if not request.user.has_perm('cms.view_drafts'):
        pages = pages.filter(status=1).exclude(publish_date__gte=datetime.now())
    if len(pages.all()) > 1:
        try:
            p = pages.get(language_code=translation.get_language())
        except:
            p = pages.get(language_code=settings.LANGUAGE_CODE)
    elif len(pages.all()) == 1:
        p = pages[0]
    else:
        raise Http404
    translation.activate(p.language_code)
    return render_page(request, p)

@csrf_protect
def render_page(request, p):
    """
    Internal interface to the page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    # If page is not pusblished and user is not admin of pages then raises 404
    if p.registration_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    if p.template_name:
        t = loader.select_template((p.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in page templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    p.title = mark_safe(p.title)
    p.content = mark_safe(p.content)

    c = RequestContext(request, {
        'page': p,
        'user': request.user,
    })
    response = HttpResponse(t.render(c))
    response.set_cookie('lang', value=translation.get_language(), max_age=(3600 * 24 * 7))
    populate_xheaders(request, response, Page, p.id)
    return response
