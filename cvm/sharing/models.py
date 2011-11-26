import datetime
import hashlib

from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.db.utils import IntegrityError


class Share(models.Model):

    hash = models.CharField(unique=True, editable=False, max_length=256, blank=True)
    resume = models.ForeignKey('cvm1.Resume', related_name='shares')
    from_date = models.DateTimeField(default=datetime.datetime.now)
    to_date = models.DateTimeField()
    email = models.EmailField()

    class Meta:
        verbose_name = _(u'share')
        verbose_name_plural = _(u'shares')

    def __unicode__(self):
        return u"%s/%s" % (self.resume, self.email)

    def get_absolute_url(self):
        return u'%s?hash=%s' % (self.resume.get_absolute_url(), self.hash)

    def _generate_hash(self):
        hash = hashlib.md5()
        hash.update(self.resume.name.encode('utf-8'))
        hash.update(self.resume.identity.name.encode('utf-8'))
        hash.update(self.resume.identity.user.username.encode('utf-8'))
        hash.update(self.email.encode('utf-8'))
        hash.update(self.from_date.isoformat().encode('utf-8'))
        hash.update(self.to_date.isoformat().encode('utf-8'))
        hash.update(datetime.datetime.now().isoformat().encode('utf-8'))
        return hash.hexdigest()


    def save(self, *args, **kwargs):
        if not self.pk:
            self.hash = self._generate_hash()
        super(Share, self).save(*args, **kwargs)
