from django.db import models


class ResumeManager(models.Manager):

    def active(self):
        return self.filter(active=True)

    def public(self):
        return self.active().filter(public=True)
