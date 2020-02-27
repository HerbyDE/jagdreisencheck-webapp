import os
import re
from datetime import datetime

from ckeditor.fields import RichTextField
from cms.models import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from django.contrib.postgres import fields
from django.utils.text import slugify
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from image_optimizer.fields import OptimizedImageField
from languages.languages import LANGUAGES
from django_google_maps import fields as map_fields

from accounts.models import IndividualProfile
from jagdreisencheck.custom_fields import ListField
from djmoney.models.fields import MoneyField
from jagdreisencheck.lists import (YNList, YNNList, ACCOMODATION_LIST, MEAL_LIST, MONTH_LIST, ONE_TO_FIVE_LIST,
                                   DOG_CHOICE_LIST, GAME_AGE_DIST_LIST, GAME_GENDER_DIST_LIST, HUNTING_TYPE_LIST,
                                   INDICATION_LIST, GAME_DENSE_LIST, INQUIRY_LIST, CALCULATION_TYPE_LIST,
                                   TRAVELLER_CHOICE_LIST, FITNESS_LIST, EXPERIENCE_LIST, YEAR_LIST, LEAD_STATUS_LIST)

TRIP_SLUG_REGEX_VALIDATOR = re.compile(r'/([a-zA-Z0-9\-]+)/([\w]{2})/([a-z0-9_]+)$')


def get_templates(directory):
    item_list = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/travelling/', directory))
    itl = list()

    for item in item_list:
        itl.append(('%s/%s' % (directory, item), item.capitalize()))

    return itl


class Game(models.Model):
    name = models.CharField(verbose_name=_('Name'), blank=False, null=False, max_length=150, unique=True)
    pub_date = models.DateTimeField(verbose_name=_('Date of Creation'), auto_now_add=True)
    created_by = models.ForeignKey(verbose_name=_('Creator'), to='accounts.User', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _('Game')
        verbose_name_plural = _('Games')
        ordering = ['name']

    def __str__(self):
        return self.name


class Trip(models.Model):
    consent_to_travel_rules = models.BooleanField(verbose_name=_('Consent to Publishing Rules'), blank=False,
                                                  null=False, default=False)
    name = models.CharField(verbose_name=_('Name'), blank=True, null=True, max_length=150)
    company = models.ForeignKey(verbose_name=_('Company'), blank=False, null=False, to='accounts.CompanyName',
                                on_delete=models.CASCADE)
    country = CountryField(verbose_name=_('Country'), blank=False, null=False)
    region = models.CharField(verbose_name=_('Region / Territory'), blank=False, null=False, max_length=300,
                              help_text=_('Please provide the territory or region name here. Please note that you may '
                                          'only offer one trip per territory or region.'))
    available_accommodation_types = ListField(verbose_name=_('Available Accommodations'), blank=True, null=True)
    private_parking = models.BooleanField(verbose_name=_('Private Parking'), blank=False, null=False, default=False,
                                          choices=YNList, help_text=_('Please indicate if hunters who arrive by car can park their car on property.'))
    airport_transfer = models.IntegerField(verbose_name=_('Airport Transfer'), blank=True, null=True, default=2,
                                           choices=YNNList)
    game = models.ManyToManyField(verbose_name=_('Game'), blank=False, to=Game)
    available_hunting_types = ListField(verbose_name=_('Hunting Types'), blank=False, null=True, default='["P"]')
    rifle_rentals = models.IntegerField(verbose_name=_('Rifle Rentals'), blank=True, null=True, default=2,
                                        choices=YNNList)
    hunting_start_time = models.IntegerField(verbose_name=_('Start of Season'), blank=True, null=True, default=5,
                                             choices=MONTH_LIST,
                                             help_text=_('Please provide the start of the hunting season.'))
    hunting_end_time = models.IntegerField(verbose_name=_('End of Season'), blank=True, null=True, default=10,
                                           choices=MONTH_LIST,
                                           help_text=_('Please provide the end of the hunting season.'))
    family_offers = models.IntegerField(verbose_name=_('Family Offers'), blank=True, null=True, default=2,
                                        choices=YNNList)
    alternative_activities = models.IntegerField(verbose_name=_('Alternative Offers'), blank=True, null=True,
                                                 default=2, choices=YNNList,
                                                 help_text=_('Is there an oportunity to spend time besides hunting activities?'))
    available_meal_options = ListField(verbose_name=_('Catering Options'), blank=True, null=True)
    staff_languages = ListField(verbose_name=_('Staff Languages'), blank=False, null=False, help_text=_('Please provide the staff languages at the hunting sight.'))
    interpreter_at_site = models.IntegerField(verbose_name=_('Interpreting Service'), blank=True, null=True,
                                              default=2, choices=YNNList, help_text=_('Please indicate if there is an interpreting service at the hunting sight.'))
    wireless_coverage = models.IntegerField(verbose_name=_('Wireless Coverage'), blank=True, null=True, default=2,
                                            choices=YNNList,
                                            help_text=_('Please indicate if hunters have mobile network access at your property.'))
    broadband_internet = models.IntegerField(verbose_name=_('Broadband Internet'), blank=True, null=True, default=2,
                                             choices=YNNList,
                                             help_text=_('Please indicate if hunters can access the internet via WiFi.'))
    vendor_link = models.URLField(verbose_name=_('Vendor Link'), blank=True, null=True)
    description = models.TextField(verbose_name=_('Trip Description'), blank=True, null=True, max_length=8000)
    more_details_pdf = models.FileField(verbose_name=_('PDF with detailed information'), blank=True, null=True,
                                        upload_to='files/trip_descriptions/')

    featured = models.BooleanField(verbose_name=_('Featured'), blank=False, null=False, default=False, choices=YNList)
    featured_start_date = models.DateTimeField(verbose_name=_('Featuring Start'), blank=True, null=True, auto_now=True)
    featured_end_date = models.DateTimeField(verbose_name=_('Featuring End'), blank=True, null=True)

    sponsored = models.BooleanField(verbose_name=_('Sponsored'), blank=False, null=False, default=False, choices=YNList)
    sponsored_start_date = models.DateTimeField(verbose_name=_('Sponsoring Start'), blank=True, null=True,
                                                auto_now=True)
    sponsored_end_date = models.DateTimeField(verbose_name=_('Sponsoring End'), blank=True, null=True)

    rating_count = models.IntegerField(verbose_name=_('Rating Count'), null=True, blank=True)
    overall_rating = models.DecimalField(verbose_name=_('Overall Rating'), max_digits=6, decimal_places=4, null=True)
    # rating_economic = models.DecimalField(verbose_name=_('Economic Rating'), max_digits=6, decimal_places=4,
    # null=True)
    rating_ecologic = models.DecimalField(verbose_name=_('Ecologic Rating'), max_digits=6, decimal_places=4, null=True)
    rating_sociocultural = models.DecimalField(verbose_name=_('Socio-Cultural Rating'), max_digits=6, decimal_places=4,
                                               null=True)
    slogan = models.CharField(verbose_name=_('Slogan'), max_length=75, null=True, blank=True)

    hunters_fitness = models.IntegerField(verbose_name=_('Suggested fitness'), null=True, choices=FITNESS_LIST,
                                          help_text=_('Please indicate the average walking distance per hunting day.'))
    hunters_experience = models.IntegerField(verbose_name=_('Suggested hunting experience'), null=True,
                                             choices=EXPERIENCE_LIST,
                                             help_text=_('Please indicate the regularity hunters should hunt in order to be prepared for the trip.'))

    address = models.CharField(verbose_name=_('Exact Address'), max_length=150, blank=True, null=True,
                               help_text=_('The Address will NOT be displayed to users. It is just for creating a google map.'))
    maps_location = map_fields.GeoLocationField(verbose_name=_('Google Geo Location'), max_length=100, blank=True, null=True)

    pub_date = models.DateTimeField(verbose_name=_('Publication Date'), blank=False, null=False, auto_now=True)
    created_by = models.ForeignKey(verbose_name=_('Creator'), to='accounts.User', on_delete=models.CASCADE,
                                   related_name='creator', null=True)
    last_modified = models.DateTimeField(verbose_name=_('Last Modified'), blank=True, null=True, auto_now=True)
    views = models.IntegerField(verbose_name=_('Views'), blank=False, null=False, default=0)

    tech_name = models.CharField(verbose_name=_('Technical Name'), max_length=30, null=True, blank=False)
    slug = models.CharField(verbose_name=_('Absolute URL'), blank=True, null=True, max_length=100)

    headline_image = OptimizedImageField(verbose_name=_('Title Image'), upload_to="trips/headline_images/", blank=True,
                                         null=True, help_text=_("Please do NOT upload images that show a lot of blood, "
                                                                "posing or other situations that may be offensive to "
                                                                "people that are not familiar with hunting!\nA title "
                                                                "pic will be displayed as background image on the trip "
                                                                "page."))
    headline_image_position = models.IntegerField(verbose_name=_('Image Y-Axis Position'), null=True, default=0)

    lead_status = models.IntegerField(verbose_name=_('Lead Status'), choices=LEAD_STATUS_LIST, default=1)

    marked_for_deletion = models.BooleanField(verbose_name=_('Marked for deletion'), default=False)

    is_approved = models.BooleanField(verbose_name=_('Trip has been approved'), default=False)
    approval_date = models.DateTimeField(auto_now=True)

    def get_available_hunting_types_display(self):
    
        res = list()
    
        if self.available_hunting_types:

            for e in self.available_hunting_types:
                for d in HUNTING_TYPE_LIST:
                    if d[0] == e:
                        res.append(d[1])
    
        return res

    def get_available_accommodation_types_display(self):

        if self.available_accommodation_types:
            result = list()
            for e in self.available_accommodation_types:
                for d in ACCOMODATION_LIST:
                    if d[0] == e:
                        result.append(d[1])

            return result
        else:
            return list()

    def get_available_meal_options_display(self):

        res = list()
        
        if self.available_meal_options:
            try:
                el = eval(self.available_meal_options)
                for e in el:
                    for d in MEAL_LIST:
                        if d[0] == e:
                            res.append(d[1])
            except TypeError or AttributeError:
                pass

        return res

    def get_staff_languages_display(self):
    
        res = list()
    
        if self.staff_languages:
            
            for e in self.staff_languages:
                for d in LANGUAGES:
                    if d[0] == e:
                        res.append(d[1])

        return res

    def get_absolute_url(self):
        return u'/portal/%s/%s/%s/' % (self.company.slug, slugify(self.country.code), self.region)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if not self.tech_name:
            self.tech_name = '{}_{}'.format(
                slugify(self.available_hunting_types[0]),
                int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
            )

        self.slug = '/{}/{}/{}/'.format(self.company.slug, slugify(self.country.code), slugify(self.region))

        if not self.views:
            self.views = 0

        if not self.featured:
            self.featured = False

        if not self.is_approved:
            self.is_approved = False

        if not self.sponsored:
            self.sponsored = False

        if not self.pub_date:
            self.pub_date = datetime.now()

        return super(Trip, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s: %s - %s' % (self.company.name, self.country.name, self.region)

    class Meta:
        verbose_name = _('Trip')
        verbose_name_plural = _('Trips')
        unique_together = ('company', 'country', 'region')
        ordering = ['name']


class Rating(models.Model):
    # Admin Data
    user = models.ForeignKey(verbose_name=_('Author'), to='accounts.User', on_delete=models.SET_NULL, null=True,
                             blank=False)
    trip = models.ForeignKey(verbose_name=_('Assiciated Trip'), to=Trip, on_delete=models.CASCADE, null=True,
                             blank=False)
    language = models.CharField(verbose_name=_('Language'), max_length=6, blank=False, null=True)
    date_created = models.DateTimeField(verbose_name=_('Creation Date'), auto_now_add=True, blank=False, null=True)
    last_modified = models.DateTimeField(verbose_name=_('Last Modified'), blank=True, null=True)
    agree_to_rules_of_contribution = models.BooleanField(verbose_name=_('Agree to Rules of Contribution'),
                                                         default=False)

    # General Data
    name = models.CharField(verbose_name=_('Title of your review'), max_length=90, blank=False, null=True)
    description = models.TextField(verbose_name=_('Detailed Trip Description'), max_length=15000, blank=True, null=True)
    nps_indication = models.PositiveIntegerField(verbose_name=_('Would you recommend the trip?'), default=3,
                                                 blank=False, null=True, choices=INDICATION_LIST)
    trophies = fields.JSONField(verbose_name=_('Trophies'), blank=True, null=True)

    # Economic Rating
    meal_option = models.CharField(verbose_name=_('Catering Option'), max_length=2, choices=MEAL_LIST, null=True,
                                   blank=False)
    meal_quality = models.IntegerField(verbose_name=_('Catering Quality'), choices=ONE_TO_FIVE_LIST, null=True,
                                       blank=True)
    accommodation_type = models.CharField(verbose_name=_('Accommodation Type'), choices=ACCOMODATION_LIST, max_length=2,
                                          default='S', null=True, blank=False)
    accommodation_rating = models.IntegerField(verbose_name=_('Accommodation Rating'), choices=ONE_TO_FIVE_LIST,
                                               null=True, blank=True, help_text=_("Please rate the accommodation you "
                                                                                   "had during your stay. Even a camping "
                                                                                   "sight may get 5 stars if everything "
                                                                                   "was fine."))
    support_with_issues = models.IntegerField(verbose_name=_('Operator Support with Issues'), choices=ONE_TO_FIVE_LIST,
                                              null=True, blank=False,
                                              help_text=_("How was the communication with the operator? Did you get "
                                                          "assistance with registering your rifle and with bureaucratic"
                                                          " processes? Were you told what vaccinations you need?"))
    price_utility = models.IntegerField(verbose_name=_('Price/Utility'), choices=ONE_TO_FIVE_LIST, null=True,
                                        blank=False)

    # Ecologic Rating
    use_of_dogs = models.BooleanField(verbose_name=_('Did you make use of dogs?'), default=False, choices=YNList)
    dog_purpose = models.CharField(verbose_name=_('What did you use the dogs for?'), max_length=3,
                                   choices=DOG_CHOICE_LIST, null=True, blank=True)
    dog_quality = models.IntegerField(verbose_name=_('Quality of dogs'), choices=ONE_TO_FIVE_LIST, null=True,
                                      blank=True)
    game_density = models.IntegerField(verbose_name=_('How dense was the wildlife?'), choices=GAME_DENSE_LIST,
                                       null=True, blank=False, help_text=_("Did you experience a good game density or "
                                                                           "was there too much/few game?"))
    game_age_dist = models.IntegerField(verbose_name=_("How was the wildlife's age distributed?"),
                                        choices=GAME_AGE_DIST_LIST, null=True, help_text=_("Were there more older or "
                                                                                           "younger pieces? Did you "
                                                                                           "experience a pyramidal "
                                                                                           "structure?"))
    game_gender_dist = models.IntegerField(verbose_name=_("How did you experience the wildlife's gender distribution?"),
                                           choices=GAME_GENDER_DIST_LIST, null=True, help_text=_("Did you experience a "
                                                                                                 "well distributed "
                                                                                                 "structure (50/50 "
                                                                                                 "female/male)?"))
    hunt_in_wilderness = models.BooleanField(verbose_name=_('Did you hunt in the wilderness?'), choices=YNList,
                                             default=False, blank=False, help_text=_("If you have pursued a gate hunt "
                                                                                     "then the game was not living in "
                                                                                     "the wild."))
    check_strike_pos = models.BooleanField(verbose_name=_('Have you had the opportunity to check your strike position?'),
                                           choices=YNList, default=False, blank=False,
                                           help_text=_("Did you have the opportunity to check your rifle and take some "
                                                       "validation shots?"))
    check_hunt_license = models.BooleanField(verbose_name=_('Was your hunting license validated?'), choices=YNList,
                                             default=False, blank=False)
    professional_hunter_quality = models.IntegerField(verbose_name=_('Quality of the professional hunter'),
                                                      choices=ONE_TO_FIVE_LIST, null=True, blank=False,
                                                      help_text=_("Please objectively rate the professional hunter's "
                                                                  "abilities and leave out personal impressions. This "
                                                                  "question is purely about his abilities."))
    organization_of_hunt = models.IntegerField(verbose_name=_('Quality of the hunting organization'),
                                               choices=ONE_TO_FIVE_LIST, null=True, blank=False,
                                               help_text=_('Please rate the hunt-related admin quality. Did your hunts '
                                                           'start on time? Were there enough vehicles? How was the '
                                                           'condition of hunting facilities?'))
    # Socio-Cultural Rating
    customer_support = models.IntegerField(verbose_name=_('Customer Support'), choices=ONE_TO_FIVE_LIST, null=True,
                                           blank=False, help_text=_('How convenient was the communication with the '
                                                                    'operator? Did the operator assist you with '
                                                                    'bureaucratic processes?'))
    hunting_introduction = models.IntegerField(verbose_name=_('Introduction to local hunting conditions'),
                                               choices=ONE_TO_FIVE_LIST, null=True, blank=False,
                                               help_text=_("How well did the operator prepare you for your hunt? Did "
                                                           "they tell you about laws and good practices?"))
    staff_languages = ListField(verbose_name=_('Languages spoken at the hunting site'), null=True, blank=False)
    communication_quality = models.IntegerField(verbose_name=_('Communication between staff and yourself'),
                                                choices=ONE_TO_FIVE_LIST, null=True, blank=False,
                                                help_text=_("How was the communication with the local employees? Did you "
                                                            "experience any inconveniences?"))
    alternative_program = models.BooleanField(verbose_name=_('Did you make use of alternative program'),
                                              choices=YNList, default=False, blank=False,
                                              help_text=_('Please indicate if you did activities besides hunting such as hiking or sightseeing.'))
    quality_alternative_program = models.IntegerField(verbose_name=_('Quality of the alternative program'),
                                                      choices=ONE_TO_FIVE_LIST, null=True, blank=True)

    # economic_rating = models.DecimalField(verbose_name=_('Economic Rating'), null=True, decimal_places=4, max_digits=5)

    ecologic_rating = models.DecimalField(verbose_name=_('Ecologic Rating'), null=True, decimal_places=4, max_digits=5)

    social_rating = models.DecimalField(verbose_name=_('Socio-Cultural Rating'), null=True, decimal_places=4,
                                        max_digits=5)

    overall_rating = models.DecimalField(verbose_name=_('Total Rating'), null=True, decimal_places=4, max_digits=5)
    
    # Peer rating regarding value
    likes = models.IntegerField(verbose_name=_('Review Likes'), null=True, blank=True, default=0)
    dislikes = models.IntegerField(verbose_name=_('Review Dislikes'), null=True, blank=True, default=0)
    
    def __str__(self):
        return u"{} - {}: {} - ID: {}".format(
            self.user.get_full_name(),
            self.trip.country.name,
            self.trip.region,
            self.pk)

    class Meta:
        unique_together = (('user', 'trip'),)
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')


class RatingReply(models.Model):
    rating = models.OneToOneField(verbose_name=_('Associated Rating'), to=Rating, on_delete=models.CASCADE, null=True,
                                  related_name='ratingreply')
    trip = models.ForeignKey(verbose_name=_('Associated Trip'), to=Trip, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(verbose_name=_('Author'), to='accounts.User', on_delete=models.SET_NULL, null=True)
    text = models.TextField(verbose_name=_('Message'), blank=False, null=True)

    class Meta:
        verbose_name = _('Rating Reply')
        verbose_name_plural = _('Rating Replies')


class Trophy(models.Model):
    game = models.ForeignKey(verbose_name=_('Game'), to=Game, blank=False, null=True, on_delete=models.CASCADE)
    weight = models.DecimalField(verbose_name=_('Weight (kg)'), max_digits=8, decimal_places=4, blank=True, null=True)
    length = models.DecimalField(verbose_name=_('Length (cm)'), max_digits=8, decimal_places=4, blank=True, null=True)
    cic_pt = models.DecimalField(verbose_name=_('CIC Points'), max_digits=8, decimal_places=4, blank=True, null=True)
    trip = models.ForeignKey(verbose_name=_('Assiciated Trip'), to=Trip, on_delete=models.CASCADE, blank=True,
                             null=True)
    rating = models.ForeignKey(verbose_name=_('Associated Rating'), to=Rating, on_delete=models.CASCADE, blank=True,
                               null=True, related_name='trophy_rating')


class TravelInquiry(models.Model):
    trip = models.ForeignKey(verbose_name=_("Trip"), to="travelling.Trip", on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name=_("User"), to=IndividualProfile, on_delete=models.SET_NULL, null=True,
                             blank=True)
    name = models.CharField(verbose_name=_("Name"), max_length=150, null=True, blank=False)
    email = models.EmailField(verbose_name=_("E-Mail"), null=True, blank=False)
    phone = models.CharField(verbose_name=_('Phone'), null=True, blank=True, max_length=35)

    # num_of_hunters = models.IntegerField(verbose_name=_("Number of Hunters"), null=True, blank=True)
    num_of_non_hunters = models.IntegerField(verbose_name=_("Number of accompanying Persons"), null=True, blank=True)

    hunting_type = models.CharField(verbose_name=_('Primary Hunting Type'), choices=HUNTING_TYPE_LIST, default='P',
                                    max_length=1)
    accommodation = models.CharField(verbose_name=_('Accommodation'), choices=ACCOMODATION_LIST, max_length=2, null=True)

    time_start = models.DateField(verbose_name=_('When would you like to start the trip?'), blank=False, null=True,
                                  error_messages={'invalid': _('Please provide a valid date. Format: dd.mm.yyyy')})
    time_end = models.DateField(verbose_name=_('When would you like to end the trip?'), blank=False, null=True,
                                error_messages={'invalid': _('Please provide a valid date. Format: dd.mm.yyyy')})

    inquiry = RichTextField(verbose_name=_("Further Details, Wishes & Questions"), null=True, blank=False)
    consent_to_be_contacted = models.BooleanField(verbose_name=_("Consent to be contacted"), default=False, blank=False)

    date = models.DateTimeField(verbose_name=_("Date of Inquiry"), auto_now_add=True)
    traveller_status = models.CharField(verbose_name=_('Travel Status'), choices=TRAVELLER_CHOICE_LIST, default='OP',
                                        max_length=2)
    read = models.BooleanField(verbose_name=_('Inquiry has been opened'), default=False, blank=False, choices=YNList)

    def __str__(self):
        string = "{}".format(self.trip.name)
        try:
            string = "{} {}".format(string, self.user.user.email)
        except AttributeError or ValueError:
            pass

        return string


class HunterDataInInquiry(models.Model):

    associated_inquiry = models.ForeignKey(verbose_name=_('Associated Inquiry'), to=TravelInquiry,
                                           on_delete=models.CASCADE)

    game = models.ForeignKey(verbose_name=_('Primary Game to hunt'), to=Game, on_delete=models.SET_NULL, null=True,
                             blank=False)
    budget = MoneyField(verbose_name=_('Budget'), blank=False, null=True, default_currency='EUR', decimal_places=2,
                        max_digits=8)
    license_since = models.IntegerField(verbose_name=_('Year the hunting license was obtained'), blank=False, null=True,
                                        choices=YEAR_LIST())
    shooting_experience = models.IntegerField(verbose_name=_('Max. Shooting distance'), blank=False, null=True)
    physical_fitness = models.IntegerField(verbose_name=_('Physical Fitness'), choices=FITNESS_LIST, null=True,
                                           blank=False)
    age = models.IntegerField(verbose_name=_('Age'), null=True, blank=True)

    def __str__(self):
        return u'%s' % self.associated_inquiry.user.user.get_full_name


# ########### Plugin Models ###########
class TripCarouselConfig(CMSPlugin):
    name = models.CharField(max_length=75, verbose_name=_('Name'), blank=False)
    application = models.CharField(max_length=75, verbose_name=_('Application'), blank=False)
    model = models.CharField(max_length=75, verbose_name=_('Database Model'), blank=False)
    num_objects = models.IntegerField(verbose_name=_('Number of Entries'), default=10, blank=False)
    set_featured = models.BooleanField(verbose_name=_('Show Featured Only'), default=False)
    set_sponsored = models.BooleanField(verbose_name=_('Show Sponsored Only'), default=False)
    selection_criteria = models.CharField(max_length=450, verbose_name=_('Selection Criteria'), null=True, blank=True)
    template = models.CharField(max_length=300, verbose_name=_('Template'), blank=False,
                                choices=[
                                    ('travelling/components/trip-thumbnail.html', _('Default Template'))
                                ])

    def __str__(self):
        return self.name


class TripBestOfModel(CMSPlugin):
    name = models.CharField(max_length=75, verbose_name=_('Name'), blank=False)
    num_objects = models.IntegerField(verbose_name=_('Number of Entries'), default=10, blank=False)
    set_featured = models.BooleanField(verbose_name=_('Show Featured Only'), default=False)
    set_sponsored = models.BooleanField(verbose_name=_('Show Sponsored Only'), default=False)
    template = models.CharField(max_length=300, verbose_name=_('Template'), blank=False,
                                choices=[('travelling/components/trip-thumbnail.html', _('Standard Template')), ],
                                default='travelling/components/trip-thumbnail.html')

    def __str__(self):
        return self.name


class TripCatalogueModel(CMSPlugin):
    name = models.CharField(verbose_name=_('Name'), max_length=75, blank=False)

    def __str__(self):
        return self.name