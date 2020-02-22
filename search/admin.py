from django.contrib import admin

from search.forms import SearchConfigAdminForm
from search.models import SearchConfig


# Register your models here.
class SearchConfigAdmin(admin.ModelAdmin):
    model = SearchConfig
    form = SearchConfigAdminForm

    class Media:
        js = ('/static/scripts/jquery.min.js', '/static/scripts/admin.js')


admin.site.register(SearchConfig, SearchConfigAdmin)
