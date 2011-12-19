from django import template

from ..models import Resume

register = template.Library()

class LatestResumesNode(template.Node):
    def __init__(self, limit=None, template_name=None, context_name=None):
        self.limit = limit
        self.template_name = template.Variable(template_name)
        self.context_name = context_name

    def render(self, context):

        object_list = Resume.objects.public()
        if self.limit:
            object_list = object_list[:self.limit]

        if self.context_name:
            context[self.context_name] = object_list
        elif self.template_name:
            context['object_list'] = object_list
        else:
            return object_list

        if self.template_name:
            template_name = self.template_name.resolve(context)
            return template.loader.render_to_string(template_name, context_instance=context)
        else:
            return ''

@register.tag
def latest_resumes(parser, token):
    """Reurns or renders a number of latest resumes.

    Syntax::

        {% latest_resumes [limit] [in <template_name>] [as <context_name>] %}
    """

    bits = token.split_contents()

    if not (bits[1] == 'as' or bits[1] == 'in'):
        limit = int(bits[1])
    else:
        limit = None

    if 'as' in bits:
        context_name = bits[bits.index('as') + 1]
    else:
        context_name = None

    if 'in' in bits:
        template_name = bits[bits.index('in') + 1]
    else:
        template_name = None

    return LatestResumesNode(limit=limit, template_name=template_name, context_name=context_name)

    raise template.TemplateSyntaxError('image tag expects a syntax of {% image <image> [<width>x<height> <mode>] [as <context_name>] %}')

@register.filter
def chunks(list, n):
    """
    Yield successive n-sized chunks from list.

    Example usage::

        {% for chunks in object_list|chunks:3 %}
        <ul class="column-of-three">
            {% for object in chunks %}
            <li>
                {{ object }}
            </li>
            {% endfor %}
        </ul>
        {% endfor %}

    """
    for i in xrange(0, len(list), n):
        yield list[i:i+n]
        

@register.filter
def swapby(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
