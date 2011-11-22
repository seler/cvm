from django.contrib import admin
from .models import Avatar, Identity, IdentityField

class IdentityAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_editable = ()
    search_fields = ()
    date_hierarchy = None
    save_as = True
    save_on_top = True
    paginator = Paginator
    inlines = []

admin.site.register(Avatar)
