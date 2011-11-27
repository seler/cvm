from django.db import models
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField('auth.User')
    name = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name or unicode(self.user)
