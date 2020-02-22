from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from slideshow.models import SlideShow


# Register your models here.
class SlideShowAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    readonly_fields = ['target_model', 'identifier', 'date_created', 'date_modified', 'owner']
    fieldsets = (
        (None, {'fields': ['name']}),
        (_('Read-Only'), {'fields': ['target_model', 'identifier', 'date_created', 'date_modified', 'owner']})
    )


admin.site.register(SlideShow, SlideShowAdmin)