# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User

class Identity(models.Model):
	user = models.ForeignKey(User)

	# these fields will require respective User fields to be mandatory [?]
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
	creation_date = models.DateTimeField(verbose_name=u'Data stworzenia', default=datetime.datetime.now)
	mod_date = models.DateTimeField(verbose_name=u'Data modyfikacji', default=datetime.datetime.now)
	# template_variant?
	# sections?

# Seperate classes for pointed and dated Sections and SectionEntries?
