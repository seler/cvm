import datetime

from django.db import models

Q = models.Q
NOW = datetime.datetime.now

class ResumeManager(models.Manager):
    def active(self):
        """Only active resumes"""
        return self.filter(active=True)

    def public(self):
        """Only active and public resumes"""
        return self.active().filter(public=True)

    def qs_for_view(self, request, username, slug, id):
        """Special queryset for view.
        
        Allows to view Resume only if:
            - user is superuser (admin)
            - user is owner of Resume
            - if resume is public
            - given hash is valid"""
        qs = self.active().filter(identity__user__username=username, slug=slug, id=id)
        if not request.user.is_superuser:
            qs = qs.filter(
                       Q(identity__user__id=request.user.id) |
                       (Q(shares__hash=request.GET.get('hash')) & Q(shares__from_date__lte=NOW) & Q(shares__to_date__gte=NOW)) |
                       Q(public=True)
            ).distinct()
        return qs
