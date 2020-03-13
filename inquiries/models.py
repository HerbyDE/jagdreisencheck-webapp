from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField
from djmoney.models.fields import MoneyField

from accounts.models import User, CorporateProfile, generate_short_uuid4
from jagdreisencheck.lists import *
from travelling.models import Trip, Game


# Create your models here.
class TripInquiry(models.Model):
    
    iq = models.CharField(verbose_name=_('Inquiry ID'), max_length=30, null=True, blank=False, unique=True)

    trip = models.ForeignKey(verbose_name=_('Associated Trip'), blank=False, null=True, to=Trip,
                             on_delete=models.SET_NULL)
    user = models.ForeignKey(verbose_name=_('Inquiring User'), blank=False, null=False, to=User,
                             on_delete=models.CASCADE)

    name = models.CharField(verbose_name=_("Name"), max_length=150, null=True, blank=True)
    email = models.EmailField(verbose_name=_("E-Mail"), null=True, blank=True)
    phone = models.CharField(verbose_name=_('Phone'), null=True, blank=True, max_length=35)

    # num_of_hunters = models.IntegerField(verbose_name=_("Number of Hunters"), null=True, blank=True)
    num_of_non_hunters = models.IntegerField(verbose_name=_("Number of accompanying Persons"), null=True, blank=True)

    hunting_type = models.CharField(verbose_name=_('Primary Hunting Type'), choices=HUNTING_TYPE_LIST, default='P',
                                    max_length=1)
    accommodation = models.CharField(verbose_name=_('Accommodation'), choices=ACCOMODATION_LIST, max_length=2,
                                     null=True)

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
    
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        
        if not self.iq:
            self.iq = generate_short_uuid4()
            
        return super(TripInquiry, self).save(force_insert, force_insert, using, update_fields)

    def __str__(self):
        string = ""
        try:
            string = "{}".format(self.trip.name)
        except TypeError or AttributeError or ValueError:
            pass
        
        try:
            string = "{} {}".format(string, self.user.user.email)
        except AttributeError or ValueError:
            pass

        return string


class HunterData(models.Model):
    inquiry = models.ForeignKey(verbose_name=_('Associated Inquiry'), to=TripInquiry,
                                on_delete=models.CASCADE)

    game = models.ManyToManyField(verbose_name=_('Primary Game to hunt'), to=Game, blank=False)
    budget = MoneyField(verbose_name=_('Budget'), blank=False, null=True, default_currency='EUR', decimal_places=2,
                        max_digits=8)
    license_since = models.IntegerField(verbose_name=_('Year the hunting license was obtained'), blank=False, null=True,
                                        choices=YEAR_LIST())
    shooting_experience = models.IntegerField(verbose_name=_('Max. Shooting distance'), blank=False, null=True)
    physical_fitness = models.IntegerField(verbose_name=_('Physical Fitness'), choices=FITNESS_LIST, null=True,
                                           blank=False)
    age = models.IntegerField(verbose_name=_('Age'), null=True, blank=True)
    
    name = models.CharField(verbose_name=_('Name'), max_length=75, null=True, blank=True)

    def __str__(self):
        return u'%s' % self.inquiry.user.get_full_name


