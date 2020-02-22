from django.forms import models, forms, SelectMultiple, TextInput, Select, DateInput
from django.utils.translation import ugettext_lazy as _
from recaptcha3.fields import ReCaptchaField

from travelling.models import Trip
from inquiries.models import TripInquiry, HunterData
from jagdreisencheck.custom_fields import JRCMoneyWidget


class CustomDateInput(DateInput):
    input_type = 'date'


class TripInquiryForm(models.ModelForm):
    recaptcha = ReCaptchaField()
    
    class Meta:
        model = TripInquiry
        fields = ['phone', 'num_of_non_hunters', 'hunting_type', 'accommodation', 'time_start',
                  'time_end', 'inquiry', 'consent_to_be_contacted', 'recaptcha', 'name', 'email']
        widgets = {
            'time_start': CustomDateInput(),
            'time_end': CustomDateInput(),
        }
        
        
class HunterDataForm(models.ModelForm):

    class Meta:
        model = HunterData
        fields = ['game', 'budget', 'license_since', 'shooting_experience', 'physical_fitness', 'age', 'name']
        widgets = {
            'budget': JRCMoneyWidget(attrs={'label': _('Budget')}),
            'game': SelectMultiple(attrs={'hide_add_btns': True, 'multiple': True}),
            'name': TextInput(attrs={'no_label': True})
        }
        
        
class HunterDataFormset(models.BaseInlineFormSet):
    
    def clean(self):
        return super(HunterDataFormset, self).clean()
    
    
class ChangeInquiryStatusForm(models.ModelForm):
    
    class Meta:
        model = Trip
        fields = ['lead_status']
        widgets = {
            'lead_status': Select(attrs={'no_label': True, 'is_submit': True})
        }
