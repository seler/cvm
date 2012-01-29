from django import template
from django.conf import settings
from cms.models import Page
from django.utils.translation import ugettext as _
from django.utils import translation
from django.contrib.auth.models import User
from datetime import datetime

register = template.Library()


class PageNode(template.Node):
    def __init__(self, context_name, user=None):
        self.context_name = context_name
        if user:
            self.user = template.Variable(user)
        else:
            self.user = None

    def render(self, context):
        pages = Page._tree_manager.filter(sites__id=settings.SITE_ID)

        # If the provided user is not authenticated, or no user
        # was provided, filter the list to only public pages.
        if self.user:
            user = self.user.resolve(context)
            if not user.is_authenticated():
                pages = pages.filter(registration_required=False)
            if not user.has_perm('cms.view_drafts'):
                pages = pages.filter(status=1).exclude(publish_date__gte=datetime.now())
        else:
            pages = pages.filter(registration_required=False, status=1).exclude(publish_date__gte=datetime.now())

        for p in pages:
            if not p.show_in_menu():
                pages = pages.exclude(pk=p.pk)

        pages = pages.filter(language_code=translation.get_language())

        context[self.context_name] = pages
        return ''


def get_pages(parser, token):
    """
    Retrieves all page objects available for the current site and
    visible to the specific user (or visible to all users if no user is
    specified). Populates the template context with them in a variable
    whose name is defined by the ``as`` clause.

    An optional ``for`` clause can be used to control the user whose
    permissions are to be used in determining which flatpages are visible.

    Syntax::

        {% get_pages [for user] as context_name %}

    Example usage::

        {% get_pages as pages %}
        {% get_pages for someuser as pages %}
    """
    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                       "['url_starts_with'] [for user] as context_name" %
                       dict(tag_name=bits[0]))
   # Must have at 3-5 bits in the tag
    if len(bits) >= 3 and len(bits) <= 5:

        # The very last bit must be the context name
        if bits[-2] != 'as':
            raise template.TemplateSyntaxError(syntax_message)
        context_name = bits[-1]

        # If there are 5 bits, there is a user defined
        if len(bits) == 5:
            if bits[-4] != 'for':
                raise template.TemplateSyntaxError(syntax_message)
            user = bits[-3]
        else:
            user = None

        return PageNode(context_name, user=user)
    else:
        raise template.TemplateSyntaxError(syntax_message)

register.tag('get_pages', get_pages)
