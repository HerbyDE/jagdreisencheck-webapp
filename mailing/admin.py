from django.contrib import admin
from mailing.models import CustomerLoyaltyElement, MailingList


# Register your models here.
class LoyaltyElementAdmin(admin.ModelAdmin):

    fields = ['file', 'link_description', 'description', 'corporate']
    readonly_fields = ['name']


class MailingListAdmin(admin.ModelAdmin):
    fieldsets = ['name', 'date_created', 'date_modified']
    readonly_fields = ['subscribers']



admin.site.register(CustomerLoyaltyElement, LoyaltyElementAdmin)
admin.site.register(MailingList)