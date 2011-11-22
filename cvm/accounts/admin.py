from django.contrib import admin
from .models import Identity, IdentityField
from .templatetags.image import process_image
from django.utils.translation import ugettext_lazy as _

class IdentityFieldAdminInline(admin.TabularInline):
    model = IdentityField


class IdentityAdmin(admin.ModelAdmin):
    list_display = ('system_name', 'avatar_image', 'user')
    list_filter = ('user',)
    list_select_related = True
    search_fields = ('name',)
    save_as = True
    save_on_top = True
    inlines = [IdentityFieldAdminInline, ]

    def avatar_image(self, object):
        return u'<img src="%s"/>' % process_image(object.avatar, 80, 80, 1)

    avatar_image.short_description = _(u'avatar')
    avatar_image.allow_tags = True

admin.site.register(Identity, IdentityAdmin)
