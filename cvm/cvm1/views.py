from django.views.generic import DetailView

from .models import Resume

class ResumeDetailView(DetailView):
    queryset = Resume.objects.public()

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(identity__user__username=self.kwargs.get('username'))
        return DetailView.get_object(self, queryset=queryset)

    def get_template_names(self):
        return [self.object.get_template_name()]
