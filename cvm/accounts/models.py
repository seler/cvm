from django.db import models
from django.utils.translation import ugettext_lazy as _


class Identity(models.Model):
    system_name = models.CharField(verbose_name=_(u'system name'),
                                   help_text=_("""put here anything so you can 
                                   identify your identity"""), max_length=64)
    user = models.ForeignKey('auth.User', verbose_name=_(u'user'))
    avatar = models.ImageField(upload_to='avatar', verbose_name=_(u'avatar'), blank=True)


    class Meta:
        verbose_name = _(u'identity')
        verbose_name_plural = _(u'identities')

    def __unicode__(self):
        return self.system_name


class IdentityField(models.Model):
    TYPE_STRING = 0
    TYPE_EMAIL = 1
    TYPE_URL = 2
    TYPE_CHOICES = (
        (TYPE_STRING, _(u'string')),
        (TYPE_STRING, _(u'email address')),
        (TYPE_STRING, _(u'url address'))
    )
    identity = models.ForeignKey('Identity', verbose_name=_('identity'))
    name = models.CharField(max_length=64, verbose_name=_(u'field name'))
    value = models.CharField(max_length=512, verbose_name=_(u'field value'))
    type = models.SmallIntegerField(verbose_name=_(u'field type'), choices=TYPE_CHOICES, default=TYPE_STRING)


    class Meta:
        verbose_name = _(u'identity field')
        verbose_name_plural = _(u'identity fields')

    def __unicode__(self):
        return self.name
