from django.contrib import admin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import mark_safe

from accounts.models import IndividualProfile, CorporateProfile, User, CompanyName, Group, Permission


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_company', 'is_superuser', 'is_staff', 'is_moderator', 'date_joined']
    list_filter = ['is_company', 'is_superuser', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': [('email', 'is_company'), ('first_name', 'last_name', 'company_name')]}),
        (_('Permissions'), {'fields': [('is_active', 'is_moderator', 'is_staff', 'is_superuser')]}),
        (_('More Details'), {'fields': [('country_of_residence', 'agree_to_tos', 'agree_to_privacy')]}),
        (_('Keys and Tokens'), {'fields': [('activation_key', 'reset_token', 'numeric_key')]}),
        (_('Admin Data'), {'fields': [('date_joined', 'last_login', 'share_link', 'id')]})
    )
    readonly_fields = ['id', 'date_joined', 'last_login', 'share_link']


class IndividualProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date', 'years_as_active_hunter', 'profile_visibility', 'search_visibility',
                    'email_newsletter', 'data_dump_requested', 'data_dump_date']
    list_filter = ['user__email', 'email_newsletter', 'data_dump_requested']
    search_fields = ['user__email', 'birth_date']
    fieldsets = (
        (None, {'fields': ('user', 'gender', 'birth_date')}),
        (_('Hunting'), {'fields': (('hunting_license', 'years_as_active_hunter'), 'countries_visited_for_hunting',
                                   ('preferred_hunting_type', 'preferred_rifle_type'))}),
        (_('Further Personal Details'), {'fields': ('info', ('profile_pic', 'title_pic'),
                                                    ('profile_visibility', 'search_visibility'),
                                                    ('profile_pic_visibility', 'title_pic_visibility'),
                                                    ('email_visibility', 'email_newsletter'))}),
        (_('Privacy Data'), {'fields': ('data_dump_requested', 'data_dump_date', 'data_dump_count')})
    )


class CorporateProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'get_company_name', 'contact_email', 'homepage']
    list_display_links = ['company_name', 'get_company_name']
    list_filter = ['country']
    search_fields = ['company_name', 'admin__email']
    fieldsets = (
        (None, {'fields': ['id', 'contact_email']}),
        (_('Admin'), {'fields': ['admin', 'has_lead_contract']}),
        (_('Public Information'), {'fields': [
            'company_name',
            ('address', 'zip_code', 'country'),
            ('phone', 'homepage'),
            ('business_hours_start', 'business_hours_end', 'business_hours_break_start', 'business_hours_break_end')
        ]}),
        (_('Profile Data'), {'fields': ['description', 'title_pic']})

    )
    readonly_fields = ['id']
    
    def company_name(self, obj):
        name = obj.company_name
        
        return name
    
    company_name.allow_tags = True
    company_name.short_description = _('Name')
    
    def get_company_name(self, obj):
        name = obj.company_name
        
        format_values = {
            'link': reverse('admin:accounts_companyname_change', args=[name.pk])
        }
        
        return mark_safe('<a href="{link}">Link</a>'.format(**format_values))

    get_company_name.allow_tags = True
    get_company_name.short_description = _('Company Name Instance')
    

class CompanyNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_profile', 'get_creator', 'created_at']
    search_fields = ['name']
    fieldsets = (
        (None, {'fields': ('name', 'has_profile')}),
        (_('Additional Details'), {'fields': ['created_by', 'slug', 'logo']})
    )
    
    def get_creator(self, obj):
        user = obj.created_by
        if user:
            format_values = {
                'link': reverse('admin:accounts_user_change', args=[user.pk]),
                'email': user.email
            }
            return mark_safe('<a href="{link}">{email}</a>'.format(**format_values))
        else:
            return '-'
        
    def get_profile(self, obj):
        try:
            profile = CorporateProfile.objects.get(company_name=obj)
            format_values = {
                'link': reverse('admin:accounts_corporateprofile_change', args=[profile.pk]),
                'profile': _('Link')
            }
            
            return mark_safe('<a href="{link}"><i class="icon-tick"></i> {profile}</a>'.format(**format_values))
            
        except CorporateProfile.DoesNotExist:
            return mark_safe('<i class="icon-cross" style="color: #d49d9d;"></i>')
        
    get_creator.allow_tags = True
    get_profile.allow_tags = True

    get_creator.short_description = _('Created By')
    get_profile.short_description = _('Profile')
    

admin.site.register(User, UserAdmin)
admin.site.register(IndividualProfile, IndividualProfileAdmin)
admin.site.register(CorporateProfile, CorporateProfileAdmin)
admin.site.register(CompanyName, CompanyNameAdmin)
admin.site.register(Group)
admin.site.register(Permission)
