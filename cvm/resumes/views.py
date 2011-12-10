from xhtml2pdf import pisa

from django.conf import settings
from django.views.generic import DetailView, ListView
from django.http import HttpResponse

from .models import Resume

class ResumeDetailView(DetailView):
    def get_queryset(self):
        self.queryset = Resume.objects.qs_for_view(self.request, self.kwargs.get('username'), self.kwargs.get('slug'))
        return self.queryset._clone()

    def get_template_names(self):
        return [self.object.get_template_name()]
    
    def get_context_data(self, **kwargs):
        context_data = super(ResumeDetailView, self).get_context_data(**kwargs) 
        context_data['TEMPLATE_STATIC_URL'] = settings.STATIC_URL + r'%s/' % self.object.template_variant.template.slug
        return context_data

    def serve_pdf(self):
        location = os.path.join(settings.MEDIA_ROOT, self.object.get_pdf_filename())
        pdf = open(location, 'rb')
        content = pdf.read()
        pdf.close()
        resp = HttpResponse(content, mimetype='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename=printout.pdf'
        return resp

class ResumeListView(ListView):
    queryset = Resume.objects.public()
