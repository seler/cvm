from django.db import models
from django.utils.translation import ugettext_lazy as _


class Avatar(models.Model):
    image = models.ImageField(upload_to='avatar', verbose_name=_(u'image'))
    name = models.CharField(max_length=64, verbose_name=_(u'field name'))


    class Meta:
        verbose_name = _(u'avatar')
        verbose_name_plural = _(u'avatars')

    def __unicode__(self):
        return self.image.name

class Identity(models.Model):
    user = models.ForeignKey('auth.User', verbose_name=_(u'user'))
    avatar = models.ForeignKey('Avatar', verbose_name=_(u'user'))


    class Meta:
        verbose_name = _(u'identity')
        verbose_name_plural = _(u'identities')

class IdentityField(models.Model):
    identity = models.ForeignKey('Identity', verbose_name=_('identity'))
    name = models.CharField(max_length=64, verbose_name=_(u'field name'))
    value = models.CharField(max_length=512, verbose_name=_(u'field value'))


    class Meta:
        verbose_name = _(u'identity field')
        verbose_name_plural = _(u'identity fields')
