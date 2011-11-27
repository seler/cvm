from django.db import models
from django.utils.translation import ugettext_lazy as _


class Identity(models.Model):
    # TODO: move to app resumes (cvm1)
    name = models.CharField(verbose_name=_(u'name'), max_length=256,
                            help_text=_("Your first and last name."))
    occupation = models.CharField(verbose_name=_(u'occupation'),
                                  max_length=256, blank=True)
    user = models.ForeignKey('auth.User', verbose_name=_(u'user'))
    avatar = models.ImageField(upload_to='avatar', verbose_name=_(u'avatar'),
                               blank=True)

    class Meta:
        verbose_name = _(u'identity')
        verbose_name_plural = _(u'identities')

    def __unicode__(self):
        return '%s, %s' % (self.name, self.occupation)

    def get_email(self):
        try:
            email_qs = IdentityField.objects.filter(type=IdentityField.TYPE_EMAIL, identity=self)[:1]
            email = email_qs.get()
        except IdentityField.DoesNotExist:
            email = self.user.email
        return email


    def get_fields(self):
        fields = []
        for field in self.identity_fields.all():
            fields.append(field.name, field.value, field.get_type_display())
        return fields

    def get_field_names(self):
        names = []
        for field in self.identity_fields.all():
            names.append(field.name)
        return names

    def get_field_values(self):
        values = []
        for field in self.identity_fields.all():
            values.append(field.value)
        return values


class IdentityField(models.Model):
    TYPE_STRING = 0
    TYPE_EMAIL = 1
    TYPE_URL = 2
    TYPE_CHOICES = (
        (TYPE_STRING, _(u'text')),
        (TYPE_STRING, _(u'email address')),
        (TYPE_STRING, _(u'url address'))
    )
    identity = models.ForeignKey('Identity', verbose_name=_('identity'), related_name='identity_fields')
    name = models.CharField(max_length=64, verbose_name=_(u'field name'))
    value = models.CharField(max_length=512, verbose_name=_(u'field value'))
    type = models.SmallIntegerField(verbose_name=_(u'field type'),
                                    choices=TYPE_CHOICES, default=TYPE_STRING)

    class Meta:
        verbose_name = _(u'identity field')
        verbose_name_plural = _(u'identity fields')

    def __unicode__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField('auth.User')
    name = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name or unicode(self.user)
