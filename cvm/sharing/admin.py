from django.conf import settings
from django.contrib import admin
from .models import Share

class ShareAdmin(admin.ModelAdmin):
    readonly_fields = ('hash',)

admin.site.register(Share, ShareAdmin)
