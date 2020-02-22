import functools
import operator
from itertools import chain

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, reverse
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.models import CompanyName, CorporateProfile
from travelling.models import Trip, Game
from django_countries.data import COUNTRIES
from search.forms import TripSearchForm


# Create your views here.
def trip_search():
    trips = Trip.objects.all()

    countries = dict()
    companies = dict()
    game_list = dict()

    for trip in trips:
        if trip.country.code in countries:
            countries[trip.country.code]["count"] += 1
        else:
            countries[trip.country.code] = {"name": trip.country.name, "count": 1}

        if trip.company.pk in companies:
            companies[trip.company.pk]["count"] += 1
        else:
            companies[trip.company.pk] = {"name": trip.company.name, "count": 1}

        for game in trip.game:
            if game.pk in game_list:
                game_list[game.pk]["count"] += 1
            else:
                game_list[game.pk] = {"name": game.name, "count": 1}

    sorted_countries = {country: countries[country] for country in sorted(countries.keys())}
    sorted_companies = {company: companies[company] for company in sorted(companies.keys())}
    sorted_wildlifes = {game: countries[game] for game in sorted(game_list.keys())}
    
    return {"companies": sorted_companies, "countries": sorted_countries, "games": sorted_wildlifes}


def generate_view(request):

    data = dict()
    countries = list()
    sorted_countries = dict()
    trips = Trip.objects.filter(is_approved=True)

    if request.user.is_authenticated and request.user.is_company:
        trips = trips.filter(company=CorporateProfile.objects.get(admin=request.user).company_name)
    
    for trip in trips:
        if trip.country.name in sorted_countries:
            sorted_countries[trip.country.name]['count'] += 1
        else:
            sorted_countries[trip.country.name] = {'code': trip.country.code, 'count': 1}
            
    sorted_countries = {country: sorted_countries[country] for country in sorted(sorted_countries.keys())}
    
    for key in sorted_countries.keys():
        if not key == "":
            countries.append({'pk': sorted_countries[key]['code'], 'name': key})
        
    data["countries"] = countries
    data['form'] = TripSearchForm
    data['trip_count'] = trips.count()

    return data


@login_required
def fetch_model_fields(request):
    '''
    Provides Model fields depending on application and model to Django Admin and Django CMS Configuration.
    Can be used with other apps as well but needs to be configured in main.js.
    Output delivers a JSON Dict as follows: (tech_name, Display Name (localized)).
    :param request: Takes the Request Object from AJAX request.
    :return: Delivers a JSON Dict.
    '''
    if request.method == 'GET':
        fields = Trip._meta.get_fields()

        field_list = list()
        for f in fields:
            name = f.name.split(sep='_')
            data_name = ''
            for n in name:
                if data_name == '':
                    data_name = n.capitalize()
                else:
                    data_name = data_name + ' ' + n.capitalize()

            field_list.append((f.name, data_name))

        data = {
            'data': field_list
        }

        return JsonResponse(data)


def retrieve_results(request):

    template = 'search/results/results-page.html'
    page = request.GET.get('page', 1)
    
    country = request.GET.get('country', None)
    game = request.GET.get('game', None)
    company = request.GET.get('company', None)

    context = dict()
    countries = list()
    sorted_countries = dict()
    trips = Trip.objects.filter(is_approved=True)

    context["form"] = TripSearchForm
    context["objects"] = trips

    for trip in Trip.objects.all():
        if trip.country.name in sorted_countries:
            sorted_countries[trip.country.name]['count'] += 1
        else:
            sorted_countries[trip.country.name] = {'code': trip.country.code, 'count': 1}

    sorted_countries = {country: sorted_countries[country] for country in sorted(sorted_countries.keys())}

    for key in sorted_countries.keys():
        if not key == "":
            countries.append({'pk': sorted_countries[key]['code'], 'name': key})

    context["countries"] = countries

    if country or game or company:

        queryset = list()

        if company and company != "":
            if request.user.is_authenticated:
                if not request.user.is_company:
                    queryset.append(Q(**{"company": company}))
                    context["company"] = CompanyName.objects.get(pk=request.GET.get("company", None))

            else:
                queryset.append(Q(**{"company": company}))
                context["company"] = CompanyName.objects.get(pk=request.GET.get("company"))

        if country and country != "":
            queryset.append(Q(**{"country": country}))
            try:
                context["country"] = COUNTRIES[country]
                context["country_key"] = {'pk': country, 'name': COUNTRIES[country]}
            except KeyError:
                pass

        if game and game != "":
            queryset.append(Q(**{"game": game}))
            context["game"] = Game.objects.get(pk=request.GET.get("game"))

        trips = Trip.objects.all()

        trips = trips.filter(functools.reduce(operator.and_, queryset))

    if request.user.is_authenticated and request.user.is_company:
        trips = trips.filter(
            company=CorporateProfile.objects.get(
                admin=request.user).company_name).order_by("-overall_rating", "rating_count", "company__name")
        
    if len(trips) == 0:
        
        if country:
            context['similar_country'] = Trip.objects.filter(country__iexact=country)
        if game:
            context['similar_game'] = Trip.objects.filter(game=game)
            
        if company:
            context['similar_company'] = Trip.objects.filter(company=company)
        
    has_rating_list = trips.filter(overall_rating__isnull=False).order_by("-overall_rating", "rating_count", "company__name")
    no_rating_list = trips.filter(overall_rating__isnull=True).order_by("country")
    
    final_list = list(chain(has_rating_list, no_rating_list))

    paginator = Paginator(final_list, settings.PAGINATOR_NUMBER)

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        elements = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        elements = paginator.page(paginator.num_pages)

    context['objects'] = elements
    context['querystrings'] = {
        'company': request.GET.get("company"),
        'game': request.GET.get("game"),
        'country': request.GET.get("country")
    }

    return render(request=request, context=context, template_name=template)


def list_trips_per_country(request, country_name):
    
    template = 'listings/country-list.html'
    page = request.GET.get('page', 1)
    
    # Reverse dict. Only possible as names are unique and hashable.
    rev_countries = dict(zip(COUNTRIES.values(), COUNTRIES.keys()))
    
    try:
        country = rev_countries[country_name.capitalize()]
    except KeyError:
        return HttpResponseRedirect(reverse('search:retrieve_search_results'))
    
    trips = Trip.objects.filter(country__iexact=country)
    
    if len(trips) == 0:
        return HttpResponseRedirect(reverse('search:retrieve_search_results'))

    has_rating_list = trips.filter(overall_rating__isnull=False).order_by("-overall_rating", "rating_count",
                                                                          "company__name")
    no_rating_list = trips.filter(overall_rating__isnull=True).order_by("country")

    final_list = list(chain(has_rating_list, no_rating_list))

    paginator = Paginator(final_list, settings.PAGINATOR_NUMBER)

    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        elements = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        elements = paginator.page(paginator.num_pages)
        
    if trips.count() == 1:
        headline = _('{} hunting trip to {} found').format(trips.count(), country_name.capitalize())
    else:
        headline = _('{} hunting trips to {} found').format(trips.count(), country_name.capitalize())
    
    context = {
        'objects': elements,
        'headline': headline,
        'page_title': _('Hunting trips to {}').format(country_name.capitalize()),
        'country': country
        
    }
    
    return render(request=request, context=context, template_name=template)


def list_trips_per_company(request, company_name):
    # TODO: LIST PER COMPANY & REMOVE ACCOUNTS BY SETTING ROBOTS CORRECTLY.
    template = 'listings/country-list.html'
    page = request.GET.get('page', 1)
    
    # Reverse dict. Only possible as names are unique and hashable.
    rev_countries = dict(zip(COUNTRIES.values(), COUNTRIES.keys()))
    
    try:
        country = rev_countries[company_name.capitalize()]
    except KeyError:
        return HttpResponseRedirect(reverse())
    
    trips = Trip.objects.filter(country__iexact=country)
    
    has_rating_list = trips.filter(overall_rating__isnull=False).order_by("-overall_rating", "rating_count",
                                                                          "company__name")
    no_rating_list = trips.filter(overall_rating__isnull=True).order_by("country")
    
    final_list = list(chain(has_rating_list, no_rating_list))
    
    paginator = Paginator(final_list, settings.PAGINATOR_NUMBER)
    
    try:
        elements = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        elements = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        elements = paginator.page(paginator.num_pages)
    
    context = {
        'objects': elements,
        'headline': _('Hunting trips to {}'.format(company_name.capitalize())),
        'country': country
        
    }
    
    return render(request=request, context=context, template_name=template)


def prefetch_trips(request):
    
    country = request.GET.get('country', None)
    company = request.GET.get('company', None)
    game = request.GET.get('game', None)
    
    trips = Trip.objects.filter(is_approved=True)
    
    if request.user.is_authenticated and request.user.is_company:
        trips = trips.filter(company=CorporateProfile.objects.get(admin=request.user).company_name)
    
    if country:
        trips = trips.filter(country__iexact=country)
    
    if company:
        trips = trips.filter(company_id=company)
        
    if game:
        trips = trips.filter(game=game)
        
    return JsonResponse({'count': trips.count()})
