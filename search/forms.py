from django.forms import models
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from search.models import SearchConfig
from travelling.models import Trip


class SearchConfigAdminForm(models.ModelForm):
    class Meta:
        model = SearchConfig
        fields = '__all__'
        widgets = {
            'fields': widgets.SelectMultiple(attrs=None)
        }


class TripSearchForm(models.ModelForm):

    class Meta:
        model = Trip
        fields = ["country", "game", "company"]
        widgets = {
            "country": widgets.Select(attrs={"hide_add_btns": True, "no_label": True, "required": False,
                                             "label": _("All countries")}),
            "game": widgets.Select(attrs={"hide_add_btns": True, "no_label": True, "required": False,
                                          "label": _("All game")}),
            "company": widgets.Select(attrs={"hide_add_btns": True, "no_label": True, "required": False,
                                             "label": _("All companies")}),
        }