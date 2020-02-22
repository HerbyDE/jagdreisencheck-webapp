from django.forms import models, forms, widgets, fields, ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django.db.utils import ProgrammingError

from jagdreisencheck.custom_fields import JRCMoneyWidget
from pricing.models import PriceList, PackageTour, Price, GamePrice, AccommodationPrice, OtherPrice


class CustomDateInput(widgets.DateInput):
    input_type = 'date'


class HandlePriceListForm(models.ModelForm):
    
    class Meta:
        model = PriceList
        fields = ['title', 'validityFrom', 'validityTo', 'is_active']
        widgets = {
            'validityFrom': CustomDateInput(),
            'validityTo': CustomDateInput(),
            'is_active': widgets.CheckboxInput(),
        }
        

class HandlePackageTourForm(models.ModelForm):
    
    class Meta:
        model = PackageTour
        fields = ['name', 'description', 'validityFrom', 'validityTo', 'is_active']
        widgets = {
            'validityFrom': CustomDateInput(),
            'validityTo': CustomDateInput()
        }
        
        
class HandlePriceForm(models.ModelForm):
    
    class Meta:
        model = Price
        fields = ['cost']
        
        
class HandleAccommodationPriceForm(models.ModelForm):
    cost = fields.CharField(label=_('Price'), widget=JRCMoneyWidget(attrs={'label': _('Price')}))
    
    class Meta:
        model = AccommodationPrice
        fields = ['accommodation', 'period', 'other_period', 'comment']


class HandleGamePriceForm(models.ModelForm):
    cost = fields.CharField(label=_('Price'), widget=JRCMoneyWidget(attrs={'label': _('Price')}))
    
    class Meta:
        model = GamePrice
        fields = ['game', 'kind', 'billing_range', 'otherRange', 'minRange', 'maxRange', 'comment']
        
        
def text_opts():
    try:
        return [('O', _('Other'))] + list(((opt.text, opt.text) for opt in OtherPrice.objects.all().distinct()))
    except ProgrammingError or AttributeError or OtherPrice.DoesNotExist:
        return []


class HandleOtherPriceForm(models.ModelForm):
    other_text = fields.CharField(label=_('Other title'), required=False)
    cost = fields.CharField(label=_('Price'), widget=JRCMoneyWidget(attrs={'label': _('Price')}))
    
    class Meta:
        
        model = OtherPrice
        fields = ['text', 'billing_range', 'minRange', 'maxRange', 'comment']
        widgets = {
            'text': widgets.Select(choices=text_opts())
        }