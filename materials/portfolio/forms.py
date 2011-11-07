# -*- coding: utf-8 -*- 
from itertools import chain

from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from portfolio.models import PortfolioCategory, Portfolio, Album, News, Region, TimedItem

class ContactForm(forms.Form):
    subject = forms.CharField(label=u'Temat')
    body = forms.CharField(label=u'Treść', widget=forms.Textarea)
    portfolio = forms.IntegerField(u'Portfolio', widget=forms.HiddenInput)

class RenderedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        items = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            items.append((name, option_value, option_label, rendered_cb, label_for, option_value in str_values))
        filters = getattr(self, '_filters', {})
        return mark_safe(render_to_string('portfolio/widgets/checkboxselectmultiple.html', {'items': items, 'filters': filters}))

class FilterForm(forms.ModelForm):
    work_type = forms.MultipleChoiceField(choices=PortfolioCategory.WORK_TYPE, widget=RenderedCheckboxSelectMultiple)
    category = forms.MultipleChoiceField(choices=PortfolioCategory.CATEGORY, widget=RenderedCheckboxSelectMultiple)
    query = forms.CharField(initial='szukaj w portfolio')
    country = forms.ModelChoiceField(queryset=Region.objects.filter(type=Region.REGION_COUNTRY).order_by('name'))
    voyvodship = forms.ModelChoiceField(queryset=Region.objects.filter(type=Region.REGION_VOYVODSHIP).order_by('name'))
    city = forms.ModelChoiceField(queryset=Region.objects.filter(type=Region.REGION_CITY).order_by('name'))

    class Meta:
        model = Portfolio

    def __init__(self, data=None, *args, **kwargs):
        super(FilterForm, self).__init__(data, *args, **kwargs)
        if data:
            region = Region.get_root_nodes()[0]
            self.fields['country'].queryset = region.get_descendants().filter(type=Region.REGION_COUNTRY).order_by('name')
            country = data.get('country', None)
            if country:
                try:
                    region = region.get_descendants().get(pk=country)
                except Region.DoesNotExist:
                    pass
                else:
                    self.fields['voyvodship'].queryset = region.get_descendants().filter(type=Region.REGION_VOYVODSHIP).order_by('name')
                    self.fields['city'].queryset = region.get_descendants().filter(type=Region.REGION_CITY).order_by('name')
            voyvodship = data.get('voyvodship', None)
            if voyvodship:
                try:
                    region = region.get_descendants().get(pk=voyvodship)
                except Region.DoesNotExist:
                    pass
                else:
                    self.fields['city'].queryset = region.get_descendants().filter(type=Region.REGION_CITY).order_by('name')
            city = data.get('city', None)
            if city:
                try:
                    region = region.get_descendants().get(pk=city)
                except Region.DoesNotExist:
                    pass
            categories = list(PortfolioCategory.objects.filter(portfolio__region__in=Region.get_tree(region)).values('work_type', 'category'))
            work_types = set([int(category['work_type']) for category in categories])
            self.fields['work_type'].choices = [(key, value) for key, value in PortfolioCategory.WORK_TYPE if key in work_types]


class UserEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Hasło', required=False)
    re_password = forms.CharField(widget=forms.PasswordInput(), label='Powtórz hasło', required=False)
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email')

    def clean_re_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['re_password']:
            raise forms.ValidationError(u'Podane hasła są różne.')
        if self.cleaned_data['password'] and len(self.cleaned_data['password']) < 5:
            raise forms.ValidationError(u"Podane hasło jest za krótkie, minimalna dlugość to 5 znaków.")
        return self.cleaned_data['re_password']

class UserForm(UserEditForm):
    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email')

class PortfolioForm(forms.ModelForm):
    country = forms.CharField(label=u'Państwo', required=False)
    voyvodship = forms.CharField(label=u'Województwo/region', required=False)
    city = forms.CharField(label=u'Miasto', required=False)
    school = forms.CharField(label=u'Szkoła', required=False)
    class Meta:
        model = Portfolio
        fields = ('avatar', 'photo', 'lead_photo', 'who_am_i', 'what_am_i_doing', 'clients', 'address', 'phone', 'fax', 'facebook', 'www')

class CVForm(forms.ModelForm):
    country = forms.CharField(label=u'Państwo', required=False, help_text=u"""<p>
        - podaj swoją lokalizację (miejsce zamieszkania lub prowadzonej 
        działalności), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu 
        Portfolia lub pracodawca.
    </p>""")
    voyvodship = forms.CharField(label=u'Województwo/region', required=False, help_text=u"""<p>
        - podaj swoją lokalizację (miejsce zamieszkania lub prowadzonej 
        działalności), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu 
        Portfolia lub pracodawca.
    </p>""")
    city = forms.CharField(label=u'Miasto', required=False, help_text=u"""<p>
        - podaj swoją lokalizację (miejsce zamieszkania lub prowadzonej 
        działalności), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu 
        Portfolia lub pracodawca.
    </p>""")
    school = forms.CharField(label=u'Szkoła', required=False, help_text=u"""<p>
        - podaj nazwę swojej szkoły (której jesteś uczniem, studentem, lub 
        absolwentem), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu 
        Portfolia lub pracodawca.
    </p>""")
    class Meta:
        model = Portfolio
        fields = ('avatar', 'photo', 'lead_photo', 'who_am_i', 'what_am_i_doing', 'clients')

class EditContactForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ('address', 'phone', 'fax', 'facebook', 'www')

class ArchiRadioRenderer(widgets.RadioFieldRenderer):
    def render(self):
        return mark_safe(u'\n'.join([force_unicode(w) for w in self]))

class AlbumForm(forms.ModelForm):
    folder = forms.CharField(label=u'Folder', required=False)
    class Meta:
        model = Album
        exclude = ('folder', 'photo_gallery', 'video_gallery', 'audio_gallery', 'comment_count')
        widgets = {
            'portfolio': forms.HiddenInput(),
            'album_type': forms.RadioSelect(renderer=ArchiRadioRenderer),
        }

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('pub_date',)
        widgets = {
            'portfolio': forms.HiddenInput(),
        }

class TimedItemForm(forms.ModelForm):
    start = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=widgets.DateInput(format='%d/%m/%Y'), label=u'Rozpoczęcie')
    end = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=widgets.DateInput(format='%d/%m/%Y'), required=False, label=u'Ukończenie')
    class Meta:
        model = TimedItem

class EducationTimedItemForm(TimedItemForm):
    start = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=widgets.DateInput(format='%d/%m/%Y'), label=u'Rozpoczęcie szkoły')
    end = forms.DateField(input_formats=['%d/%m/%Y', '%Y-%m-%d'], widget=widgets.DateInput(format='%d/%m/%Y'), required=False, label=u'Ukończenie szkoły')
