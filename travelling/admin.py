from django.urls import reverse
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.text import mark_safe

from travelling.forms import TripAdminForm
from travelling.models import Trip, Game, Rating
from travelling.resources import TripResource

from import_export.admin import ImportExportModelAdmin


# Register your models here.
class TripAdmin(ImportExportModelAdmin):
    form = TripAdminForm
    resource_class = TripResource
    list_display = ['company', 'country', 'region', 'get_created_by_link', 'featured', 'sponsored', 'is_approved',
                    'pub_date']
    list_display_links = ['company', 'country', 'region', 'get_created_by_link']
    
    list_filter = ['company', 'country', 'region', 'is_approved', 'pub_date']
    search_fields = ['company', 'country', 'region', 'created_by']
    fieldsets = (
        (None, {'fields': (('name', 'company'), ('country', 'region'))}),
        (_('Hunting-related Data'), {'fields': (('game', 'available_hunting_types', 'rifle_rentals'),
                                                ('hunting_start_time', 'hunting_end_time'))}),
        (_('Accommodation Data'), {'fields': (('available_accommodation_types', 'available_meal_options'),
                                              ('airport_transfer', 'alternative_activities', 'family_offers'),
                                              ('private_parking', 'staff_languages', 'interpreter_at_site'),
                                              ('wireless_coverage', 'broadband_internet'))}),
        (_('Description'), {'fields': ['description']}),
        (_('Admin Data'), {'fields': (('vendor_link', 'slogan'), ('featured', 'featured_start_date', 'featured_end_date'),
                                      ('sponsored', 'sponsored_start_date', 'sponsored_end_date'),
                                      ('created_by', 'pub_date', 'last_modified'),
                                      ('slug', 'headline_image'))})
    )
    readonly_fields = ['featured_start_date', 'featured_end_date', 'sponsored_start_date', 'sponsored_end_date',
                       'pub_date', 'created_by', 'last_modified', 'created_by']
    
    def get_created_by_link(self, obj):
        user = obj.created_by
        
        if user:
            link = reverse('admin:accounts_user_change', args=[user.pk])
            
            format_val = {'link': link, 'email': user.email}
            
            return mark_safe('<a href="{link}">{email}</a>'.format(**format_val))
        else:
            return '-'
    
    get_created_by_link.allow_tags = True
    get_created_by_link.short_description = _('Created By')


class GameAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']

    readonly_fields = ['created_by', 'pub_date']


class TripImportExportAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Trip, TripAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Rating)