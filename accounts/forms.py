from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.forms import models, fields, PasswordInput, TextInput, SelectMultiple, widgets, ValidationError, DateInput
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_countries.data import COUNTRIES
from jagdreisencheck.custom_fields import JRCMoneyWidget
from recaptcha3.fields import ReCaptchaField
from django.contrib.auth.hashers import check_password

from accounts.models import IndividualProfile, CorporateProfile, User, CompanyName
from jagdreisencheck.lists import DAY_CHOICE_LIST, YEAR_LIST
from travelling.models import TravelInquiry, HunterDataInInquiry


class CustomDateInput(DateInput):
    input_type = 'date'


class CreateBaseUserInstance(models.ModelForm):
    confirm_passwd = fields.CharField(label=_('Confirm Password'), widget=PasswordInput, required=True)
    recaptcha = ReCaptchaField()

    def clean_confirm_passwd(self):
        passwd = self.cleaned_data['password']
        cf_psw = self.cleaned_data['confirm_passwd']

        if passwd == cf_psw:
            self.cleaned_data['password'] = make_password(password=passwd)
            return self.cleaned_data
        else:
            raise ValidationError(_('The passwords do not match.'))

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_passwd', 'first_name', 'last_name', 'country_of_residence',
                  'agree_to_privacy', 'agree_to_tos', 'referred_by']
        exclude = ['groups', 'user_permissions', 'is_active', 'is_superuser', 'is_staff', 'is_moderator', 'is_company',
                   'date_joined', 'last_login', 'activation_key', 'reset_token', 'numeric_key', 'share_link']
        widgets = {
            'password': PasswordInput,
            'agree_to_privacy': widgets.CheckboxInput(attrs={'required': True}),
            'agree_to_tos': widgets.CheckboxInput(attrs={'required': True}),
            'referred_by': widgets.HiddenInput(attrs={'required': False})
        }
        help_texts = {
            'email': _('Please provide your e-mail address that you will use to log in.'),
            'country_of_residence': _("Please provide the country you're living in here."),
        }


class CreateIndividualProfileForm(models.ModelForm):
    class Meta:
        model = IndividualProfile
        fields = ['gender', 'birth_date', 'hunting_license', 'years_as_active_hunter', 'email_newsletter']
        exclude = ['user', 'data_dump_requested', 'data_dump_date', 'data_dump_count', 'preferred_hunting_type',
                   'preferred_rifle_type', 'info', 'profile_pic', 'title_pic', 'countries_visited_for_hunting']
        widgets = {
            'countries_visited_for_hunting': SelectMultiple(choices=COUNTRIES, attrs={'multiple': True}),
            'hunting_license': widgets.Select(attrs={'required': True}),
            'birth_date': CustomDateInput(attrs={'placeholder': _('dd.mm.yyyy')}),
        }


class CreateCompanyInstance(models.ModelForm):
    class Meta:
        model = CompanyName
        fields = ['name']
        exclude = ['created_by', 'has_profile', 'contact_email']


class CreateCompanyNameInTripCreationForm(models.ModelForm):
    class Meta:
        model = CompanyName
        fields = ['name']
        exclude = ['created_at', 'created_by', 'has_profile', 'logo', 'contact_email']


class CreateCorporateProfileForm(models.ModelForm):
    company_name = TextInput(attrs={'label': _('Company Name')})

    class Meta:
        model = CorporateProfile
        fields = ['address', 'zip_code', 'city', 'country', 'phone', 'contact_email', 'homepage',
                  'main_lang_of_conversation', 'operator_type']
        exclude = ['company_name', 'admin', 'logo', 'description']
        widgets = {
            'contact_email': widgets.EmailInput(
                attrs={'placeholder': _('e.g. info@jagdreisencheck.de'), 'required': True})
        }


class ChangeProfilePictureForm(models.ModelForm):
    class Meta:
        model = IndividualProfile
        fields = ['profile_pic']


class ChangeProfileDescriptionForm(models.ModelForm):
    class Meta:
        model = IndividualProfile
        fields = ['info']


class TravelInquiryForm(models.ModelForm):

    def clean_time_start(self):

        today = datetime.today()
        date = self.cleaned_data['time_start']

        if not date >= today:
            raise ValidationError(_('The start date must be in th future.'), code='invalid')
        else:
            return self.cleaned_data['time_start']

    def clean_time_end(self):

        if 'time_start' in self.cleaned_data.keys() and 'time_end' in self.cleaned_data.keys():

            data = self.cleaned_data
            start = data['time_start']
            end = data['time_end']

            if not start <= end:
                raise ValidationError(_('The start date must be before the end date.'), code='invalid')
            else:
                return self.cleaned_data['time_end']

    class Meta:
        model = TravelInquiry
        fields = ['name', 'email', 'num_of_non_hunters', 'hunting_type', 'accommodation',
                  'time_start', 'time_end', 'inquiry', 'consent_to_be_contacted', 'phone']
        exclude = ['date', 'trip', 'user']
        widgets = {
            'time_start': widgets.DateInput(attrs={'placeholder': _('dd.mm.yyyy')}),
            'time_end': widgets.DateInput(attrs={'placeholder': _('dd.mm.yyyy')}),
            'consent_to_be_contacted': widgets.CheckboxInput(attrs={'required': True})
        }


class AddHunterToInquiryForm(models.ModelForm):

    def clean_budget(self):
        data = self.cleaned_data

        if not data['game'] and not data['shooting_experience'] and not data['age']:
            data['budget'] = None

        return data

    def clean_physical_fitness(self):
        data = self.cleaned_data

        if not data['game'] and not data['shooting_experience'] and not data['age']:
            data['physical_fitness'] = None

        return data

    def clean_license_since(self):
        data = self.cleaned_data

        if not data['game'] and not data['shooting_experience'] and not data['age']:
            data['license_since'] = None

        return data

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m

        data = self.cleaned_data

        if not data['game']:
            pass
        else:
            return self.instance

    class Meta:
        model = HunterDataInInquiry
        fields = ['game', 'budget', 'license_since', 'shooting_experience', 'physical_fitness', 'age']
        widgets = {
            'game': widgets.SelectMultiple(attrs={'hide_add_btns': True, 'multiple': True}),
            'budget': JRCMoneyWidget(attrs={'label': _('Budget per Hunter'), 'placeholder': _('e.g. 2300')}),
        }


class UpdateTravelInquiryForm(models.ModelForm):
    class Meta:
        model = TravelInquiry
        fields = ['traveller_status']


class ResetPasswordByEmailForm(models.ModelForm):
    recaptcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ['email']


class ResetPasswordByTokenForm(models.ModelForm):
    confirm_password = fields.CharField(label=_('Confirm password'), widget=widgets.PasswordInput, required=True)
    token = fields.HiddenInput(attrs={'type': 'hidden'})
    recaptcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': widgets.PasswordInput()
        }


############  UPDATE FORMS  #############
class UpdateBaseUserInstance(models.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'country_of_residence']
        exclude = ['groups', 'user_permissions', 'is_active', 'is_superuser', 'is_staff', 'is_moderator', 'is_company',
                   'date_joined', 'last_login', 'activation_key', 'reset_token', 'numeric_key', 'share_link']
        widgets = {
            'password': PasswordInput,
            'agree_to_privacy': widgets.Select(attrs={'required': True}),
            'agree_to_tos': widgets.Select(attrs={'required': True}),
            'email': widgets.TextInput(attrs={'disabled': True})
        }


class UpdateIndividualProfileForm(models.ModelForm):
    class Meta:
        model = IndividualProfile
        fields = ['gender', 'birth_date', 'hunting_license', 'years_as_active_hunter', 'countries_visited_for_hunting',
                  'info', 'profile_pic', 'title_pic']
        exclude = ['user', 'data_dump_requested', 'data_dump_date', 'data_dump_count', 'preferred_hunting_type',
                   'preferred_rifle_type']
        widgets = {
            'birth_date': CustomDateInput(attrs={'placeholder': _('dd.mm.yyyy')}),
            'countries_visited_for_hunting': SelectMultiple(choices=COUNTRIES, attrs={'multiple': True}),
            'hunting_license': widgets.Select(attrs={'required': True}),
            'years_as_active_hunter': widgets.Select(choices=YEAR_LIST())
        }


class UpdateCorporateProfileContactForm(models.ModelForm):
    class Meta:
        model = CorporateProfile
        fields = ['phone', 'contact_email', 'business_hours_days', 'business_hours_start', 'business_hours_end',
                  'business_hours_break_start', 'business_hours_break_end', 'address', 'zip_code', 'city', 'country',
                  'main_lang_of_conversation']
        widgets = {
            'business_hours_days': widgets.SelectMultiple(attrs={'multiple': True}, choices=DAY_CHOICE_LIST)
        }
        labels = {
            'main_lang_of_conversation': _('Primary conversation language')
        }


class UpdateCorporateProfileInformationForm(models.ModelForm):
    class Meta:
        model = CorporateProfile
        fields = ['description', 'homepage', 'title_pic', 'operator_type']


class UpdateCompanyLogoForm(models.ModelForm):
    class Meta:
        model = CompanyName
        fields = ['logo']


class UpdatePrivacySettingsForm(models.ModelForm):
    class Meta:
        model = IndividualProfile
        fields = ['profile_visibility', 'search_visibility', 'profile_pic_visibility', 'title_pic_visibility',
                  'email_visibility', 'email_newsletter']


class ChangePasswordForm(models.ModelForm):
    old_password = fields.CharField(label=_('Old Password'), widget=PasswordInput, required=True)
    confirm_password = fields.CharField(label=_('Confirm New Password'), widget=PasswordInput, required=True)
    
    def clean(self):
        
        old_pw = self.cleaned_data['old_password']
        new_pw = self.cleaned_data['password']
        con_pw = self.cleaned_data['confirm_password']
        
        if not new_pw == con_pw:
            raise ValidationError(_('The new passwords do not match.'), code='invalid')
        
        if not check_password(old_pw, self.instance.password):
            raise ValidationError(_('The old password is invalid.'), code='invalid')
        
        return super(ChangePasswordForm, self).clean()
        
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': widgets.PasswordInput(attrs={'required': True, })
        }
        labels = {
            'password': _('New password')
        }
