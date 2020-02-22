from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from travelling.models import Trip
from django_countries.data import COUNTRIES


def get_trip_from_url(company, country, region):
    
    if len(country) == 2:
        country = slugify(COUNTRIES[country])
        
    slug = '/{}/{}/{}/'.format(company, country, region)
    
    trip = get_object_or_404(Trip, slug=slug)
    
    return trip
