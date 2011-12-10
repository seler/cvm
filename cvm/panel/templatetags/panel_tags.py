from django.conf import settings
from django import template
from django.template.loader import get_template, select_template
from django.template.defaultfilters import slugify

register = template.Library()

class GetFieldsNode(template.Node):
    def __init__(self, obj, context_name=None):
        self.obj = template.Variable(obj)
        self.context_name = context_name

    def render(self, context):
        obj = self.obj.resolve(context)
        fields = [(field.name, field.value_to_string(obj)) for field in obj._meta.fields]

        if self.context_name:
            context[self.context_name] = fields
            return ''
        else:
            return fields


@register.tag
def get_fields(parser, token):
    bits = token.split_contents()

    if len(bits) == 4 and bits[2] == 'as':
        return GetFieldsNode(bits[1], context_name=bits[3])
    elif len(bits) == 2:
        return GetFieldsNode(bits[1])
    else:
        raise template.TemplateSyntaxError("get_fields expects a syntax of "
                       "{% get_fields <obj> [as <context_name>] %}")

class SectionDetailNode(template.Node):
    def __init__(self, section):
        self.section = template.Variable(section)

    def render(self, context):
        section = self.section.resolve(context)
        context['section'] = section
        context['entry_list'] = section.section_entries.all()
        template_name = 'panel/tags/section_%s.html' % slugify(section.get_type_display()) 
        t = get_template(template_name)
        self.nodelist = t.nodelist
        return self.nodelist.render(context)

@register.tag
def section_detail(parser, token):
    bits = token.split_contents()
    
    if len(bits) == 2:
        return SectionDetailNode(bits[1])
    
    raise template.TemplateSyntaxError("get_fields expects a syntax of "
                       "{% sction_detail <section> %}")