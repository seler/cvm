# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User

class Identity(models.Model):
	user = models.ForeignKey(User)

	# these fields will require respective User fields to be mandatory
	first_name = models.CharField(verbose_name=u'Imię', default=user.first_name)
	last_name = models.CharField(verbose_name=u'Nazwisko', default=user.last_name)
	email = models.EmailField(verbose_name=u'Adres e-mail', default=user.email)
	
	phone = models.CharField(verbose_name=u'Telefon')
	address = models.TextField(verbose_name=u'Adres')
	# region?
	# others?

class Resume(models.Model):
	# scrapped User field, since Identity is linked to User

	identity = models.ForeignKey(Identity)
	# photo?
	creation_date = models.DateTimeField(verbose_name=u'Data stworzenia', auto_now_add=True)
	mod_date = models.DateTimeField(verbose_name=u'Data modyfikacji', auto_now=True)
	# template_variant?

class Section(models.Model):
	SEC_TYPES = list(enumerate([u'', u'wypunktowana', u'datowana', u'słownikowa']))

	resume = models.ForeignKey(Resume)
	title = models.CharField(verbose_name=u'Tytuł sekcji')
	sec_type = models.PositiveSmallIntegerField(verbose_name=u'Typ sekcji', choices=SEC_TYPES)

class SectionEntry(models.Model):
	section = models.ForeignKey(Section)
	from_date = models.DateField(verbose_name=u'Od', blank=True) # datowana
	to_date = models.DateField(verbose_name=u'Do', blank=True) # datowana
	title = models.CharField(verbose_name=u'Przedmiot wpisu', blank=True) # słownikowa
	content = models.CharField(verbose_name=u'Treść wpisu')

class Template(models.Model):
	name = models.CharField()

class TemplateVariant(models.Model):
	template = models.ForeignKey(Template)
	name = models.CharField()
