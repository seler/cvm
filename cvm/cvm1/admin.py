from .models import *
from django.contrib import admin

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

admin.site.register(Resume, ResumeAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateVariant, TemplateVariantAdmin)
