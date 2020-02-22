from fastnumbers import fast_real

from django.template import Context, Library, Template

try:
    from django_languages.languages import LANGUAGES
except KeyError or ImportError:
    from languages.languages import LANGUAGES

from django.utils.html import escape, mark_safe

from jagdreisencheck.lists import HUNTING_TYPE_LIST
from travelling.models import Game, Rating, Trip

import re

register = Library()


@register.simple_tag(name='get_primary_hunting_type')
def get_primary_hunting_type(inp):
    ht = list()

    if type(inp).__name__ == 'list':
        input_list = inp
    else:
        input_list = eval(inp)

    for e in input_list:
        for h in HUNTING_TYPE_LIST:
            if e == h[0]:
                ht.append(h[1])

    return ht[0]


@register.simple_tag()
def get_game(val):
    try:
        return Game.objects.get(pk=val)
    except Game.DoesNotExist or ValueError:
        pass


@register.simple_tag()
def get_rating_field(field, variant):
    template = Template('rating/rating-field.html')
    context = Context({
        'field': field,
        'variant': variant
    })

    return template.render(context)


@register.filter()
def get_var_type(variable):
    return type(fast_real(variable)).__name__


@register.filter()
def is_list(var):
    return type(var) == list


@register.filter()
def get_percent(field, divider):

    if field:
        value = field / divider * 100
        return round(value)
    else:
        pass


@register.simple_tag()
def display_languages(value):
    try:
        val = value
        opt = ""
        ctr = 0

        for e in val:
            for code, name in LANGUAGES:
                if code == e:
                    opt += str(name)
                    if ctr < len(val) - 1:
                        opt += ", "

            ctr += 1

        return opt

    except ValueError or TypeError:
        pass


@register.filter()
def render_safe(string):
    '''
    splitter = re.compile(r'(\s+)')
    words = splitter.split(escape(string))
    for i, b in enumerate(words):
        if not (b.startswith('&lt;meta&gt;') or b.startswith('&lt;META&gt;')
                or b.endswith('&lt;meta/&gt;') or b.endswith('&lt;META/&gt;')):
            words[i] = mark_safe(b)

    return mark_safe(''.join(words))
    '''
    return string


@register.inclusion_tag(filename='travelling/rating/display-ratings/display-all-ratings.html', takes_context=True)
def display_platform_data(context):

    trips = Trip.objects.all()
    countries = dict()

    for trip in trips:
        if trip.country.name in countries:
            countries[trip.country.name] += 1
        else:
            countries[trip.country.name] = 1

    context['rating_count'] = Rating.objects.all().count()
    context['trip_count'] = trips.count()
    context['country_count'] = len(countries.keys())

    return context
