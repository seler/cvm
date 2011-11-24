# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import ResumeManager

class Template(models.Model):
    name = models.CharField(max_length=256, verbose_name=_(u'name'))
    slug = models.SlugField(max_length=64, verbose_name=_(u'slug'))

    class Meta:
        verbose_name = _(u'template')
        verbose_name_plural = _(u'templates')

    def __unicode__(self):
        return self.name


class TemplateVariant(models.Model):
    template = models.ForeignKey('Template', verbose_name=_('template'))
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = models.SlugField(max_length=64, verbose_name=_('slug'))

    class Meta:
        verbose_name = _(u'template variant')
        verbose_name_plural = _(u'template variants')

    def __unicode__(self):
        return '%s/%s' % (self.template.name, self.name)

    def get_template_name(self):
        return '%s/%s/%s.%s' % (settings.RESUME_TEMPLATES_DIR_NAME, self.template.slug, self.slug, settings.RESUME_TEMPLATES_FORMAT)


class Resume(models.Model):
    identity = models.ForeignKey('accounts.Identity',
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

    objects = ResumeManager()

    class Meta:
        verbose_name = _(u'resume')
        verbose_name_plural = _(u'resumes')

    def validate_unique(self, exclude=None):
        # TODO: validate that resume.slug and identity.user.username 
        # are unique together
        super(Resume, self).validate_unique(self, exclude=exclude)

    def __unicode__(self):
        return '%s/%s' % (self.identity.name, self.name)

    def get_absolute_url(self):
        kwargs = {'username': self.identity.user.username, 'slug':self.slug}
        return reverse('resume_detail', kwargs=kwargs)

    def get_template_name(self):
        return self.template_variant.get_template_name()


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
    resume = models.ForeignKey('Resume', verbose_name=_(u'resume'))
    title = models.CharField(verbose_name=_(u'title'), max_length=100)
    type = models.PositiveSmallIntegerField(
            verbose_name=_(u'type'),
            choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _(u'section')
        verbose_name_plural = _(u'sections')

    def __unicode__(self):
        return '%s/%s' % (self.resume, self.title)


class SectionEntry(models.Model):
    section = models.ForeignKey(Section)
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

