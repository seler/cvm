# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


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
    slug = models.SlugField(max_length=256, verbose_name=_('name'))


    class Meta:
        verbose_name = _(u'variant')
        verbose_name_plural = _(u'variants')

    def __unicode__(self):
        return '%s/%s' % (self.template.name, self.name)


class Resume(models.Model):
    identity = models.ForeignKey('accounts.Identity')
    name = models.CharField(verbose_name=_(u'resume_name'), max_length=50)
    creation_date = models.DateTimeField(verbose_name=_(u'creation_date'), auto_now_add=True)
    mod_date = models.DateTimeField(verbose_name=_(u'mod_date'), auto_now=True)
    template_variant = models.ForeignKey(TemplateVariant)
    active = models.BooleanField()
    public = models.BooleanField()


    class Meta:
        verbose_name = _(u'resume')
        verbose_name_plural = _(u'resumes')

    def __unicode__(self):
        return '%s/%s' % (self.identity.system_name, self.name)


class Section(models.Model):
    SEC_TYPES = list(enumerate([u'', u'wypunktowana', u'datowana', u'słownikowa']))  # TODO: ustawic stale zamiast enumerte

    resume = models.ForeignKey('Resume')
    title = models.CharField(verbose_name=_(u'section_title'), max_length=100)
    sec_type = models.PositiveSmallIntegerField(verbose_name=_(u'section_type'), choices=SEC_TYPES)

    class Meta:
        verbose_name = _(u'section')
        verbose_name_plural = _(u'sections')

    def __unicode__(self):
        return '%s/%s' % (self.resume, self.title)


class SectionEntry(models.Model):
    section = models.ForeignKey(Section)	
    from_date = models.DateField(verbose_name=_(u'from_date'), blank=True) # datowana
    to_date = models.DateField(verbose_name=_(u'to_date'), blank=True) # datowana
    title = models.CharField(verbose_name=_(u'entry_title'), blank=True, max_length=100) # słownikowa
    content = models.CharField(verbose_name=_(u'entry_content'), max_length=255)

    class Meta:
        verbose_name = _(u'entry')
        verbose_name_plural = _(u'entries')

    def __unicode__(self):
        return '%s/%s' % (self.section, self.title)

