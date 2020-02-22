import re

from django.forms import models, widgets, forms
from django.utils.translation import ugettext_lazy as _
from djmoney.forms.widgets import MoneyWidget
from languages import languages
from django_google_maps import widgets as map_widgets

from jagdreisencheck.lists import HUNTING_TYPE_LIST, INDICATION_LIST, ACCOMODATION_LIST, MEAL_LIST
from jagdreisencheck.custom_fields import JRCMoneyWidget
from travelling.models import Trip, Game, Rating, Trophy, RatingReply
from recaptcha3.fields import ReCaptchaField


class CreateATripForm(models.ModelForm):
    recaptcha = ReCaptchaField()

    class Meta:
        model = Trip
        fields = ['consent_to_travel_rules', 'company', 'country', 'region', 'airport_transfer', 'game',
                  'available_hunting_types', 'hunting_start_time', 'hunting_end_time', 'staff_languages',
                  'interpreter_at_site', 'rifle_rentals']
        exclude = ['name', 'available_accommodation_types', 'private_parking', 'family_offers',
                   'alternative_activities',
                   'available_meal_options', 'description', 'featured', 'featured_start_date', 'featured_end_date',
                   'sponsored', 'sponsored_end_date', 'sponsored_start_date', 'reviewed', 'reviewed_by', 'pub_date',
                   'created_by', 'last_modified', 'views', 'slug', 'wireless_coverage', 'broadband_internet', 'slogan',
                   'placeholder_additional_info']
        widgets = {
            'consent_to_travel_rules': widgets.CheckboxInput(attrs={'required': True}),
            'staff_languages': widgets.SelectMultiple(choices=languages.LANGUAGES, attrs={'multiple': True}),
            'game': widgets.SelectMultiple(attrs={'multiple': True}),
            'available_hunting_types': widgets.SelectMultiple(choices=HUNTING_TYPE_LIST, attrs={'multiple': True})
        }
        help_texts = {
            'company': _("Please provide the company name here. If you can't find it in the list, please create it."),

        }


class UpdateATripForm(models.ModelForm):
    class Meta:
        model = Trip
        fields = ['country', 'region', 'airport_transfer', 'game', 'available_hunting_types', 'hunting_start_time',
                  'hunting_end_time', 'staff_languages', 'interpreter_at_site', 'vendor_link', 'rifle_rentals',
                  'available_accommodation_types', 'private_parking', 'family_offers', 'alternative_activities',
                  'available_meal_options', 'description', 'wireless_coverage', 'broadband_internet', 'headline_image',
                  'more_details_pdf', 'hunters_fitness']  # 'hunters_experience', 'maps_location', 'address'
        exclude = ['company', 'featured', 'featured_start_date', 'featured_end_date', 'sponsored', 'sponsored_end_date',
                   'sponsored_start_date', 'pub_date', 'created_by', 'last_modified',
                   'views', 'slug', 'placeholder_additional_info', 'slogan', 'name']
        widgets = {
            'consent_to_travel_rules': widgets.CheckboxInput(attrs={'required': True}),
            'staff_languages': widgets.SelectMultiple(choices=languages.LANGUAGES, attrs={'multiple': True}),
            'game': widgets.SelectMultiple(attrs={'multiple': True}),
            'available_hunting_types': widgets.SelectMultiple(choices=HUNTING_TYPE_LIST, attrs={'multiple': True}),
            'available_accommodation_types': widgets.SelectMultiple(choices=ACCOMODATION_LIST, attrs={'multiple': True,
                                                                                                      'required': True}),
            'available_meal_options': widgets.SelectMultiple(choices=MEAL_LIST, attrs={'multiple': True}),
            'description': widgets.Textarea(attrs={'warning': _('Please note that contact information is NOT allowed '
                                                                'here. The trip will be removed if the text is not '
                                                                'compliant to our <a href="/flat/tos/">Terms of '
                                                                'Service.</a>'), 'required': True}),
            # 'maps_location': map_widgets.GoogleMapsAddressWidget()
        }


class TripAdminForm(models.ModelForm):

    class Meta:
        model = Trip
        fields = '__all__'

    def clean_slug(self):
        slug = self.cleaned_data['slug']

        try:
            if bool(re.match(r'/([a-zA-Z0-9\-]+)/([\w]{2})/([a-z0-9_]+)$', slug)) is True:
                return slug
            else:
                raise forms.ValidationError(_('Invalid Slug'))
        except TypeError:
            pass


class CreateGameForm(models.ModelForm):
    class Meta:
        model = Game
        fields = ['name']
        exclude = ['pub_date', 'created_by']


class TripRatingForm(models.ModelForm):
    class Meta:
        model = Rating
        fields = ['name', 'meal_quality', 'accommodation_type', 'accommodation_rating',
                  'support_with_issues', 'price_utility', 'use_of_dogs', 'dog_purpose', 'dog_quality', 'game_density',
                  'game_age_dist', 'game_gender_dist', 'hunt_in_wilderness', 'check_strike_pos', 'check_hunt_license',
                  'professional_hunter_quality', 'customer_support', 'hunting_introduction', 'staff_languages',
                  'communication_quality', 'alternative_program', 'quality_alternative_program', 'description',
                  'meal_option', 'staff_languages', 'nps_indication', 'agree_to_rules_of_contribution', 'trophies',
                  'organization_of_hunt']
        exclude = ['user', 'trip', 'created_at', 'last_modified']
        widgets = {
            'staff_languages': widgets.SelectMultiple(choices=languages.LANGUAGES, attrs={'multiple': True,
                                                                                          'required': True}),
            'nps_indication': widgets.Select(choices=INDICATION_LIST, attrs={'required': True}),
            'agree_to_rules_of_contribution': widgets.CheckboxInput(attrs={'required': True}),
            'alternative_program': widgets.Select(attrs={'required': True}),
            'trophies': widgets.HiddenInput()
        }
        
    
class UpdateTripRatingForm(models.ModelForm):
    
    class Meta:
        model = Rating
        fields = ['agree_to_rules_of_contribution', 'description']


class ReplyToRatingForm(models.ModelForm):

    class Meta:
        model = RatingReply
        fields = ['text']
        exclude = ['rating', 'author']


class CreateTrophyForm(models.ModelForm):
    class Meta:
        model = Trophy
        fields = ['weight', 'length', 'cic_pt']
        exclude = ['game', 'trip', 'rating']


class MassTripUploadForm(forms.Form):
    file = forms.FileField(label=_('CSV File'), required=True, allow_empty_file=False)


class FindATripToRateForm(models.ModelForm):

    class Meta:
        model = Trip
        fields = ['company', 'country', 'region']
        widgets = {
            'region': widgets.Select(attrs={'required': True})
        }
        help_texts = {
            'region': ""
        }