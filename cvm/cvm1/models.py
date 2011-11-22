# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

class FakeIdentity(models.Model):
	user = models.ForeignKey(User)

	# these fields will require respective User fields to be mandatory
	first_name = models.CharField(verbose_name=_(u'first_name'), default=user.first_name)
	last_name = models.CharField(verbose_name=_(u'last_name'), default=user.last_name)
	email = models.EmailField(verbose_name=_(u'e_mail'), default=user.email)
	
	phone = models.CharField(verbose_name=_(u'phone'))
	address = models.TextField(verbose_name=_(u'address'))
	# region?
	# others?

	class Meta:
		verbose_name = _(u'identity')
		verbose_name_plural = _(u'identities')

class Resume(models.Model):
	# scrapped User field, since Identity is linked to User

	identity = models.ForeignKey('accounts.Identity')
	# photo?
	creation_date = models.DateTimeField(verbose_name=_(u'creation_date'), auto_now_add=True)
	mod_date = models.DateTimeField(verbose_name=_(u'mod_date'), auto_now=True)
	template_variant = models.ForeignKey(TemplateVariant)

	class Meta:
		verbose_name = _(u'resume')
		verbose_name_plural = _(u'resumes')

class Section(models.Model):
	SEC_TYPES = list(enumerate([u'', u'wypunktowana', u'datowana', u'słownikowa']))

	resume = models.ForeignKey(Resume)
	title = models.CharField(verbose_name=_(u'section_title'))
	sec_type = models.PositiveSmallIntegerField(verbose_name=_(u'section_type'), choices=SEC_TYPES)

	class Meta:
		verbose_name = _(u'section')
		verbose_name_plural = _(u'sections')

class SectionEntry(models.Model):
	section = models.ForeignKey(Section)
	from_date = models.DateField(verbose_name=_(u'from_date'), blank=True) # datowana
	to_date = models.DateField(verbose_name=_(u'to_date'), blank=True) # datowana
	title = models.CharField(verbose_name=_(u'entry_title'), blank=True) # słownikowa
	content = models.CharField(verbose_name=_(u'entry_content'))

	class Meta:
		verbose_name = _(u'entry')
		verbose_name_plural = _(u'entries')

class Template(models.Model):
	name = models.CharField()
	slug = 'templates/'+slugify(name)+'/'

	class Meta:
		verbose_name = _(u'template')
		verbose_name_plural = _(u'templates')

class TemplateVariant(models.Model):
	template = models.ForeignKey(Template)
	name = models.CharField()
	slug = 'templates/'+slugify(template.name)+'/'+slugify(name)+'/'

	class Meta:
		verbose_name = _(u'variant')
		verbose_name_plural = _(u'variants')
