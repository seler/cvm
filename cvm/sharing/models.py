import datetime
import hashlib

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

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
        hash.update(self.from_date.isoformat())
        hash.update(self.to_date.isoformat())
        hash.update(datetime.datetime.now().isoformat())
        return hash.hexdigest()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.hash = self._generate_hash()
            update = False
        else:
            update = True
        super(Share, self).save(*args, **kwargs)
        self.send_email(update)

    def send_email(self, update=False):
        email_to = [self.email, self.resume.identity.user.email]
        message, html_message = self._get_email_message(update=update)
        email_from = u'%s <%s>' % (self.resume.identity.name, self.resume.identity.get_email())
        subject = _(u'%s sends you his/her resume') % (self.resume.identity.name)
        msg = EmailMultiAlternatives(subject, message, email_from, email_to)
        msg.attach_alternative(html_message, "text/html")
        msg.send()

    def _get_email_message(self, update=False):
        host = 'http://%s' % Site.objects.get_current().domain
        context_vars = {'object': self, 'HOST': host, 'update': update}
        message = render_to_string('sharing/email_message.txt', context_vars)
        html_message = render_to_string('sharing/email_message.html', context_vars)
        return message, html_message
