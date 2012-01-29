from django import forms
from django.contrib import admin
from cms.models import Page
from cms.models import Photo
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import translation
from django.contrib.auth.models import User
from cms.helpers import get_language
from feincms.admin.tree_editor import TreeEditor
from django.contrib.contenttypes import generic
from tinymce.widgets import TinyMCE

class PageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100,
                regex=r'^[-\w/\.~]+$', required=False,
                help_text=_("Example: '/about/contact/'. Make sure to have "
                            "leading and trailing slashes."),
                error_message=_("This value must contain only letters, numbers,"
                            " dots, underscores, dashes, slashes or tildes."))
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    translates = forms.ModelChoiceField(queryset=Page.objects.all(),
                                    empty_label=_('[nothing]'), required=False)
    parent = TreeNodeChoiceField(queryset=Page.tree.all(),
                level_indicator=u'+--', empty_label=_('[root]'), required=False)

    class Meta:
        model = Page

    def clean_translates(self):
    	'''
    	checks whether the selected translation language is not
    	the same as an article has been originally written in
    	'''
        a = self.cleaned_data.get('translates')
        if a != None:
            if a.language_code == self.cleaned_data.get('language_code'):
                raise forms.ValidationError(_("Language of current page and "
                                        "translated page connot be the same."))
            if (self.instance not in a.translations.all() and self.cleaned_data.get('language_code') in a.get_translations_langs()):
                raise forms.ValidationError(_("This page already has translation in %s language." % (get_language(self.cleaned_data.get('language_code')))))
        return a

    def clean_url(self):
        '''
        prompts an error message if url has not been inserted
        '''
        url_type = self.cleaned_data.get('url_type')
        url = self.cleaned_data.get('url')
        if  url_type == True and len(url) == 0:
            raise forms.ValidationError(_("You must insert url or use URL type as slug."))
        return url

    def clean_parent(self):
        '''
        prompts an error message if parent page has been written in different language than this page
        '''
        parent = self.cleaned_data.get('parent')
        if parent != None:
            if parent.language_code != self.cleaned_data.get('language_code'):
                raise forms.ValidationError(_('Parent page must be the same language.'))
                return None
        return parent

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['translates'].queryset = Page.objects.filter(is_translation=False).exclude(pk=self.instance.pk)
        self.fields['parent'].queryset = Page.tree.exclude(pk=self.instance.pk)

class ImagesInline(generic.GenericTabularInline):
    model = Photo
    #max_num =4

class PageAdmin(TreeEditor, MPTTModelAdmin):
    form = PageForm
    fieldsets = (
                 (_('Language setup'), {'fields': ('language_code', 'translates')}),
                 (None, {'fields': ('parent', 'title', 'menu_name', 'slug', 'status', 'author', 'content')}),
                 (_('Advanced options'), {'classes': ('collapse',), 'fields': ('url_type', 'url', 'tags', 'publish_date', 'last_modified', 'enable_comments', 'registration_required', 'template_name', 'sites')}),
                 )
    list_filter = ('sites', 'language_code', 'registration_required', 'status')
    search_fields = ('url', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ImagesInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
    	'''
    	sets current user as default page author
    	'''
        if db_field.name == "author":
            kwargs["initial"] = User.objects.get(pk=request.user.pk)
            kwargs["empty_label"] = _('[none]')
        return super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
    	'''
    	sets current site as default page site
    	'''
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Page, PageAdmin)
#admin.site.register(Page, TreeEditor)
