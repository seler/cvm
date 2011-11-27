from django.views.generic import DetailView, ListView

from .models import Resume

class ResumeDetailView(DetailView):
    def get_queryset(self):
        self.queryset = Resume.objects.qs_for_view(self.request, self.kwargs.get('username'), self.kwargs.get('slug'))
        return self.queryset._clone()

    def get_template_names(self):
        return [self.object.get_template_name()]



class ResumeListView(ListView):
    queryset = Resume.objects.public()
