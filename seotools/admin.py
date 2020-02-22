from django.contrib import admin

from seotools.models import SEOCountryDescriptor, RegistrationInfoGraphic

# Register your models here.


class CountryDescriptorAdmin(admin.ModelAdmin):
    
    fields = ['country', 'description', 'meta_description', 'image1', 'image2', 'image3', 'keywords']
    
    
class RegistrationInfoGraphicAdmin(admin.ModelAdmin):
    
    fields = ['title', 'body', 'origin', 'order', 'image', 'date_created']
    readonly_fields = ['date_created']
    
    
admin.site.register(SEOCountryDescriptor, CountryDescriptorAdmin)
admin.site.register(RegistrationInfoGraphic, RegistrationInfoGraphicAdmin)
