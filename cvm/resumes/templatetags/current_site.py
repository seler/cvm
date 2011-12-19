from django import template

from django.contrib.sites.models import Site

register = template.Library()

class CurrentSiteNode(template.Node):
    def __init__(self, context_name=None):
        self.context_name = context_name

    def render(self, context):
        current_site = Site.objects.get_current()
        context[self.context_name] = current_site
        return ''

@register.tag
def current_site(parser, token):
    """Returns current `Site`.
    
    Usage::

        {% current_site as <context_name> %}

    """
    bits = token.split_contents()
    if bits[1] == 'as' and len(bits) == 3:
        return CurrentSiteNode(context_name=bits[2])
    raise template.TemplateSyntaxError('current_site tag expects a syntax of {% current_site as <context_name> %}')
