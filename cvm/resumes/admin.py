from .models import *
from django.contrib import admin
from .templatetags.image import process_image
from django.utils.translation import ugettext_lazy as _

class SectionEntryAdminInline(admin.TabularInline):
    model = SectionEntry

class SectionAdmin(admin.ModelAdmin):
    list_select_related = True
    inlines = [SectionEntryAdminInline, ]

class ResumeAdmin(admin.ModelAdmin):
    list_filter = ('active', 'public')
    list_select_related = True

class TemplateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TemplateVariantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class IdentityFieldAdminInline(admin.TabularInline):
    model = IdentityField


class IdentityAdmin(admin.ModelAdmin):
    list_display = ('name', 'avatar_image', 'user')
    list_filter = ('user',)
    list_select_related = True
    search_fields = ('name',)
    save_as = True
    save_on_top = True
    inlines = [IdentityFieldAdminInline, ]

    def avatar_image(self, obj):
        return u'<img src="%s"/>' % process_image(obj.avatar, 80, 80, 1)

    avatar_image.short_description = _(u'avatar')
    avatar_image.allow_tags = True

admin.site.register(Identity, IdentityAdmin)

admin.site.register(Resume, ResumeAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateVariant, TemplateVariantAdmin)
