from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from easy_thumbnails.fields import ThumbnailerImageField


# Create your models here.
class SEOCountryDescriptor(models.Model):
    
    country = CountryField(verbose_name=_('Country'), blank=False, null=False, unique=True)
    description = RichTextField(verbose_name=_('Description'), blank=False, null=True)
    meta_description = models.TextField(verbose_name=_('Meta-Description'), blank=False, null=True, max_length=140,
                                        help_text=_('Max. 140 characters.'))
    keywords = models.TextField(verbose_name=_('Keywords'), blank=False, null=True,
                                help_text=_('Separate words by comma. Generally the keywords jagdreisencheck, jagen, jagdreise, nachhaltige jagd, jagen weltweit, nachhaltigkeit are included!'))
    image1 = ThumbnailerImageField(verbose_name=_('Image 1'), blank=True, null=True)
    image2 = ThumbnailerImageField(verbose_name=_('Image 2'), blank=True, null=True)
    image3 = ThumbnailerImageField(verbose_name=_('Image 3'), blank=True, null=True)
    
    def __str__(self):
        return self.country.name
    
    class Meta:
        ordering = ['country']


REGISTRATION_ORIGINS = [
    ('create_trip', _('Trip Creation')),
    ('rate_trip', _('Trip Rating')),
    ('trip_inquiry', _('Trip Inquiry')),
    ('default', _('Default (without a page reference)'))
]


class RegistrationInfoGraphic(models.Model):
    title = models.CharField(verbose_name=_('Headline'), max_length=150, blank=False, null=True)
    body = models.TextField(verbose_name=_('Body'), blank=True, null=True,
                            help_text=_('Text displayed below the slider graphic.'))
    origin = models.CharField(verbose_name=_('User Origin'), choices=REGISTRATION_ORIGINS, max_length=15, null=True,
                              blank=False)
    order = models.PositiveIntegerField(verbose_name=_('Ordering'), blank=False, null=True)
    image = ThumbnailerImageField(verbose_name=_('Slider Image'), blank=False, null=True)
    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now=True, blank=False, null=True)
    
    def __str__(self):
        return u'{} - {}'.format(self.title, self.origin)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Registration Info Graphic')
        verbose_name_plural = _('Registration Info Graphics')
