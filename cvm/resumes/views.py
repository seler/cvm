from django.template.defaultfilters import slugify
from xhtml2pdf import pisa

from django.conf import settings
from django.views.generic import DetailView, ListView
from django.http import HttpResponse

from .models import Resume

class ResumeDetailView(DetailView):
    def get_queryset(self):
        self.queryset = Resume.objects.qs_for_view(self.request, self.kwargs.get('username'), self.kwargs.get('slug'), self.kwargs.get('object_id'))
        return self.queryset._clone()

    def get_template_names(self):
        return [self.object.get_template_name()]
    
    def get_context_data(self, **kwargs):
        context_data = super(ResumeDetailView, self).get_context_data(**kwargs) 
        context_data['TEMPLATE_STATIC_URL'] = settings.STATIC_URL + r'%s/' % self.object.template_variant.template.slug
        return context_data


class ResumePDFView(ResumeDetailView):
    def render_to_response(self, context):
        # po to, zeby zweryfikowac uzytkownika itd bo nie chce mi sie tego pisac
        super(ResumePDFView, self).render_to_response(context)
        f = self.object.get_pdf_file()
        response = HttpResponse(f.read(), mimetype='application/pdf')
        filename = slugify("%s %s" % (self.object.identity.name, self.object.slug))
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % filename
        return response

class ResumeListView(ListView):
    queryset = Resume.objects.public()
