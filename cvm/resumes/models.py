# -*- coding: utf-8 -*-
import datetime
import os

from xhtml2pdf import pisa

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.context import Context
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from .managers import ResumeManager


class Identity(models.Model):
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
        """Tries to obtain email from ``identity_fields``, defaults to
        ``user.email``"""
        try:
            email_qs = IdentityField.objects.filter(
                type=IdentityField.TYPE_EMAIL, identity=self)[:1]
            email = email_qs.get()
        except IdentityField.DoesNotExist:
            email = self.user.email
        return email

    def get_fields(self):
        """Returns list of ``IdentityField`` as tuples, each containing field
        ``name``, ``value`` and ``type`` display"""
        fields = []
        for field in self.identity_fields.all():
            fields.append(field.name, field.value, field.get_type_display())
        return fields

    def get_field_names(self):
        """Returns list of all fields names"""
        names = []
        for field in self.identity_fields.all():
            names.append(field.name)
        return names

    def get_field_values(self):
        """Returns list of all fields values"""
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
        (TYPE_EMAIL, _(u'email address')),
        (TYPE_URL, _(u'url address'))
    )
    identity = models.ForeignKey('Identity', verbose_name=_('identity'),
        related_name='identity_fields')
    name = models.CharField(max_length=64, verbose_name=_(u'field name'))
    value = models.CharField(max_length=512, verbose_name=_(u'field value'))
    type = models.SmallIntegerField(verbose_name=_(u'field type'),
                                    choices=TYPE_CHOICES, default=TYPE_STRING)

    class Meta:
        verbose_name = _(u'identity field')
        verbose_name_plural = _(u'identity fields')

    def __unicode__(self):
        return self.name


class Template(models.Model):
    name = models.CharField(max_length=256, verbose_name=_(u'name'))
    slug = models.SlugField(max_length=64, verbose_name=_(u'slug'))
    screen = models.ImageField(upload_to='template', verbose_name=_(u'screen'))

    class Meta:
        verbose_name = _(u'template')
        verbose_name_plural = _(u'templates')

    def __unicode__(self):
        return self.name


class TemplateVariant(models.Model):
    template = models.ForeignKey('Template', verbose_name=_('template'))
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = models.SlugField(max_length=64, verbose_name=_('slug'))
    screen = models.ImageField(upload_to='template', verbose_name=_(u'screen'),
        blank=True, null=True)

    class Meta:
        verbose_name = _(u'template variant')
        verbose_name_plural = _(u'template variants')

    def __unicode__(self):
        return '%s/%s' % (self.template.name, self.name)

    def get_template_name(self):
        """returns template variant filename to render to"""
        return '%s/%s/%s.%s' % (settings.RESUME_TEMPLATES_DIR_NAME,
                                self.template.slug, self.slug,
                                settings.RESUME_TEMPLATES_FORMAT)

    def get_screen(self):
        """returns screenshot of the template variant or of template if variant
        lacks it"""
        return self.screen if self.screen else self.template.screen


class Resume(models.Model):
    identity = models.ForeignKey('Identity',
                                 verbose_name=_(u'identity'))
    name = models.CharField(verbose_name=_(u'name'), max_length=256)
    slug = models.SlugField(verbose_name=_(u'slug'), max_length=64)
    creation_date = models.DateTimeField(verbose_name=_(u'creation date'),
                                         auto_now_add=True)
    modification_date = models.DateTimeField(
            auto_now=True,
            verbose_name=_(u'modification date'),)
    template_variant = models.ForeignKey(
            'TemplateVariant',
            verbose_name=_(u'template variant'),)
    active = models.BooleanField(
            verbose_name=_(u'is active'),
            default=False,)
    public = models.BooleanField(
            verbose_name=_(u'is public'),
            default=False,)
    pdf_generation_date = models.DateTimeField(editable=False, null=True)

    objects = ResumeManager()

    class Meta:
        verbose_name = _(u'resume')
        verbose_name_plural = _(u'resumes')

    def __unicode__(self):
        return '%s/%s' % (self.identity.name, self.name)

    def get_absolute_url(self):
        """returns absolute url to Resume"""
        kwargs = {'username': self.identity.user.username, 'slug': self.slug,
                  'object_id': self.id}
        return reverse('resume_detail', kwargs=kwargs)

    def get_template_name(self):
        """returns template name that resuem should be rendered to"""
        return self.template_variant.get_template_name()

    def get_pdf_filename(self):
        """returns path to pdf file"""
        username = slugify(self.identity.user.username)
        filename = 'resume/pdf/%s/%s.pdf' % (username, self.slug)
        return os.path.abspath(filename)

    def get_pdf_file(self):
        """returns pdf file instance. generates it if's not there"""
        if not self.pdf_generation_date or self.pdf_generation_date < \
                                           self.modification_date:
            self.generate_pdf()
        return open(self.get_pdf_filename())

    def get_pdf_url(self):
        """returns absolute url to pdf file"""
        kwargs = {'username': self.identity.user.username, 'slug': self.slug,
                  'object_id': self.id}
        return reverse('resume_pdf', kwargs=kwargs)

    def generate_pdf(self):
        """generates pdf"""
        t = get_template(self.get_template_name())
        c = Context({
            'object': self,
            'STATIC_URL': settings.STATIC_URL,
            'TEMPLATE_STATIC_URL': settings.STATIC_URL + r'%s/' % \
                                        self.template_variant.template.slug
        })
        filename = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
            self.get_pdf_filename()))
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        html = t.render(c)

        css = open(os.path.join(settings.MEDIA_ROOT, 'template/templates',
            self.template_variant.template.slug, 'css/default.css')).read()

        f = file(filename, 'wb')
        pisa.CreatePDF(html.encode("UTF-8"), f, encoding='UTF-8',
            default_css=css)
        f.close()
        self.pdf_generation_date = datetime.datetime.now()


class Section(models.Model):
    TYPE_DATELIST = 1         # html ul with dates?
    TYPE_DEFINITIONLIST = 2   # html dl tag
    TYPE_UNORDEREDLIST = 3    # html ul tag
    TYPE_ORDEREDLIST = 4      # html ol tag
    TYPE_CHOICES = (
         (TYPE_DATELIST, _(u'date list')),
         (TYPE_DEFINITIONLIST, _(u'definition list')),
         (TYPE_UNORDEREDLIST, _(u'bulleted list')),
         (TYPE_ORDEREDLIST, _(u'numbered list')),
    )
    resume = models.ForeignKey('Resume', verbose_name=_(u'resume'),
        related_name='sections')
    title = models.CharField(verbose_name=_(u'title'), max_length=100)
    type = models.PositiveSmallIntegerField(
            verbose_name=_(u'type'),
            choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _(u'section')
        verbose_name_plural = _(u'sections')

    def __unicode__(self):
        return u'%s/%s' % (self.resume, self.title)


class SectionEntry(models.Model):
    section = models.ForeignKey(Section, related_name='section_entries')
    from_date = models.DateField(
            verbose_name=_(u'from date'),
            blank=True,
            null=True)
    to_date = models.DateField(
            verbose_name=_(u'to date'),
            blank=True,
            null=True)
    current = models.BooleanField(default=False)
    title = models.CharField(
            verbose_name=_(u'title'),
            blank=True,
            max_length=256)
    content = models.CharField(verbose_name=_(u'content'), max_length=256)

    class Meta:
        verbose_name = _(u'entry')
        verbose_name_plural = _(u'entries')

    def __unicode__(self):
        return '%s/%s' % (self.section, self.title)
