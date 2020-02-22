from fastnumbers import fast_real

from django.template import Library
from django.utils.html import strip_tags
from django.conf import settings

try:
    from django_languages.languages import LANGUAGES
except KeyError or ImportError:
    from languages.languages import LANGUAGES

from easy_thumbnails.files import get_thumbnailer
from seotools.models import SEOCountryDescriptor


register = Library()


@register.inclusion_tag(filename='seotools/country-descriptor.html', takes_context=True)
def get_country_descriptor(context, country):
    
    country_descriptor = None
    
    try:
        country_descriptor = SEOCountryDescriptor.objects.get(country=country)
    except SEOCountryDescriptor.DoesNotExist:
        pass
    
    context['country_descriptor'] = country_descriptor
    
    return context


@register.simple_tag(takes_context=False)
def get_country_meta_info(country, selector):
    country_descriptor = None
    
    try:
        country_descriptor = SEOCountryDescriptor.objects.get(country=country)
        model_dict = country_descriptor.__dict__
        
        return strip_tags(model_dict[selector])
        
    except SEOCountryDescriptor.DoesNotExist:
        pass
    

@register.simple_tag(takes_context=False)
def get_placeholder_image(country, selector):
    try:
        country_descriptor = SEOCountryDescriptor.objects.get(country=country)
        model_dict = country_descriptor.__dict__
        
        if selector % 3 == 0:
            image = country_descriptor.image3
        elif selector % 2 == 0:
            image = country_descriptor.image2
        else:
            image = country_descriptor.image1
            
        # thumb = get_thumbnailer(image, relative_name='thumb_{}_{}'.format(country, selector))
        # opts = {'crop': True, 'size': (400, 320)}
        
        # return thumb.get_thumbnail(opts)
        return image
    
    except SEOCountryDescriptor.DoesNotExist:
        pass