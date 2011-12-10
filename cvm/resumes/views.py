from django.views.generic import DetailView, ListView
from xhtml2pdf import pisa

from .models import Resume

class ResumeDetailView(DetailView):
    def get_queryset(self):
        self.queryset = Resume.objects.qs_for_view(self.request, self.kwargs.get('username'), self.kwargs.get('slug'))
        return self.queryset._clone()

    def get_template_names(self):
        return [self.object.get_template_name()]

    def generate_pdf(self):
        html = self.as_view()
        resp = HttpResponse(content_type='application/pdf')
        pisa.CreatePDF(html.encode("UTF-8")

class ResumeListView(ListView):
    queryset = Resume.objects.public()
