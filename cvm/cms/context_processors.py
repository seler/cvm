from django.conf import settings

def feincms_admin_media(request):
    """
    Adds FEINCMS_ADMIN_MEDIA variable to the context.
    """
    return {'FEINCMS_ADMIN_MEDIA': settings.FEINCMS_ADMIN_MEDIA}