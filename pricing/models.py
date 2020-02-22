from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField

from jagdreisencheck.lists import ACCOMODATION_LIST, BILLING_PERIOD, GAME_BILLING_RANGE, GAME_GENDER_LIST
from travelling.models import Trip, Game


# Create your models here.
class PriceList(models.Model):
    trip = models.ForeignKey(verbose_name=_('Trip'), to=Trip, on_delete=models.CASCADE, related_name='assoc_trip')
    title = models.CharField(verbose_name=_('Title'), max_length=150, default=_('Prices'))
    validityFrom = models.DateField(verbose_name=_('Valid from'))
    validityTo = models.DateField(verbose_name=_('Valid until'))
    is_active = models.BooleanField(verbose_name=_('Price list active'), default=True)
    
    def __str__(self):
        return u'{}: {} - {}'.format(self.trip, self.validityFrom, self.validityTo)
    
    class Meta:
        unique_together = ('trip', 'validityFrom', 'validityTo')
        ordering = ['-is_active', '-validityFrom', '-validityTo']
        verbose_name = _('Price List')
        verbose_name_plural = _('Price Lists')
        
        
class PackageTour(models.Model):
    name = models.CharField(verbose_name=_('Package name'), max_length=75)
    description = models.TextField(verbose_name=_('Description'), max_length=500)
    validityFrom = models.DateTimeField(verbose_name=_('Valid from'))
    validityTo = models.DateTimeField(verbose_name=_('Valid until'))
    price_list = models.ForeignKey(verbose_name=_('Price list'), to=PriceList, on_delete=models.CASCADE,
                                   related_name='price_list')
    is_active = models.BooleanField(verbose_name=_('Package tour active'), default=True)
    
    class Meta:
        verbose_name = 'Package Tour'
        verbose_name_plural = 'Package Tours'
        ordering = ['-validityFrom', '-validityTo']
        
        
class Price(models.Model):
    cost = MoneyField(verbose_name=_('Cost per period'), max_digits=8, decimal_places=2)
    price_list = models.ForeignKey(verbose_name=_('Price list'), to=PriceList, on_delete=models.CASCADE, null=True,
                                   related_name='plist')
    package_tour = models.ForeignKey(verbose_name=_('Package tour'), to=PackageTour, on_delete=models.CASCADE, null=True,
                                     related_name='ptour')
    
    
class AccommodationPrice(models.Model):
    accommodation = models.CharField(verbose_name=_('Accommodation type'), max_length=2, choices=ACCOMODATION_LIST)
    price = models.ForeignKey(verbose_name=_('Price'), to=Price, on_delete=models.CASCADE)
    period = models.CharField(verbose_name=_('Billing period'), max_length=1, choices=BILLING_PERIOD)
    other_period = models.CharField(verbose_name=_('Other billing period than selectable'), max_length=150, blank=True,
                                    null=True)
    comment = models.TextField(verbose_name=_('Comments'), blank=True, null=True)
    
    
class GamePrice(models.Model):
    game = models.ForeignKey(verbose_name=_('Game'), to=Game, on_delete=models.CASCADE, related_name='game_price')
    price = models.ForeignKey(verbose_name=_('Price'), to=Price, on_delete=models.CASCADE)
    kind = models.CharField(verbose_name=_('Kind / Gender'), choices=GAME_GENDER_LIST, max_length=1, null=True)
    billing_range = models.CharField(verbose_name=_('Billing range'), max_length=1, choices=GAME_BILLING_RANGE)
    otherRange = models.CharField(verbose_name=_('Other range'), blank=True, null=True, max_length=150)
    minRange = models.IntegerField(verbose_name=_('Start of range'), default=1,
                                   help_text=_('Please only provide the numeric value here. E.g. 100 instead of 100cm'))
    maxRange = models.IntegerField(verbose_name=_('End of range'),
                                   help_text=_('Please only provide the numeric value here. E.g. 100 instead of 100cm'))
    comment = models.TextField(verbose_name=_('Comments'), blank=True, null=True)


class OtherPrice(models.Model):
    text = models.CharField(verbose_name=_('Title'), max_length=150, null=True, blank=False,
                            help_text=_("Should there be no choices available please select OTHER and provide your data"
                                        " in the appearing field."))
    price = models.ForeignKey(verbose_name=_('Price'), to=Price, on_delete=models.CASCADE)
    billing_range = models.CharField(verbose_name=_('Billing range'), blank=True, null=True, max_length=150)
    minRange = models.IntegerField(verbose_name=_('Start of range'), null=True, blank=True)
    maxRange = models.IntegerField(verbose_name=_('End of range'), null=True, blank=True)
    comment = models.TextField(verbose_name=_('Comments'), blank=True, null=True)
