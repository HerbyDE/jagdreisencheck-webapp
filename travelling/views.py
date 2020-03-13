import os
import functools
import operator

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict, modelformset_factory
from django.db.models import Q, Avg, Count, Case, When
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, reverse, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.sitemaps import Sitemap

from jagdreisencheck.decorators import login_required_with_params
from accounts.forms import CreateCompanyNameInTripCreationForm, AddHunterToInquiryForm
from accounts.models import CorporateProfile
from jagdreisencheck.lists import *
from travelling.forms import (CreateATripForm, CreateGameForm, TripRatingForm, UpdateATripForm, UpdateTripRatingForm,
                              ReplyToRatingForm)
from travelling.models import (Trip, Game, Rating, RatingReply, HunterDataInInquiry)

from inquiries.models import TripInquiry, HunterData
from pricing.views import render_price_list

from mailing.views import validate_referral, send_mail as send_complex_mail


# CRUD Views handling the trip management.
@login_required_with_params
def create_a_trip(request):
    template = 'travelling/trips/create-a-trip-page.html'
    form = CreateATripForm
    context = dict()

    if request.method == 'POST':
        if request.user.is_company:
            req_post = request.POST.copy()
            req_post['company'] = CorporateProfile.objects.get(admin=request.user).company_name.pk
        else:
            req_post = request.POST

        form = form(req_post, request.FILES)
        if form.is_valid():
            form1 = form.save(commit=False)
            form1.created_by = request.user
            form1.save()
            form.save_m2m()

            messages.success(request=request, message=_('Thanks for creating the trip!'))
            html_template = 'travelling/emails/create_trip/trip-was-added.html'

            if not settings.DEBUG or not os.environ['testsystem']:

                try:
                    company = CorporateProfile.objects.get(company_name=form1.company)

                    context = {
                        'company': company,
                        'user': company.admin,
                        'trip': form1,
                        'title': _('A trip has been created for your company'),
                        'request': request,
                    }

                    send_complex_mail(subject=_('A trip has been created for your company'),
                                      recipients=[company.contact_email], html_template=html_template, context=context)

                except CorporateProfile.DoesNotExist:
                    company = {
                        'name': "Jadreisencheck",
                        'contact_email': 'trip.verification@jagdreisencheck.de',
                        'is_jrc': True,
                    }

                    context = {
                        'company': company,
                        'trip': form1,
                        'title': _('A trip has been created for your company'),
                        'request': request,
                    }

                    send_complex_mail(subject=_('A trip has been created for your company'),
                                      recipients=[company['contact_email']], html_template=html_template,
                                      context=context)

            else:
                company = {
                    'name': "Jadreisencheck",
                    'contact_email': 'trip.verification@jagdreisencheck.de',
                    'is_jrc': True,
                }

                context = {
                    'company': company,
                    'trip': form1,
                    'email': {'title': _('A trip has been created for your company')},
                    'request': request,
                }

                send_complex_mail(subject=_('A trip has been created for your company'),
                                  recipients=[company['contact_email']], html_template=html_template, context=context)

            return HttpResponseRedirect(
                reverse('travelling:show_trip', args=(form1.company.slug,
                                                      slugify(form1.country.code),
                                                      slugify(form1.region)
                                                      )))
        else:

            context['form'] = form
            context['company_name_form'] = CreateCompanyNameInTripCreationForm

            return render(request, template, context)
    else:
        context['form'] = form
        context['company_name_form'] = CreateCompanyNameInTripCreationForm
        context['game_form'] = CreateGameForm
        return render(request, template, context)


def retrieve_trip_details(request, company, country, region):

    url = '/{}/{}/{}/'.format(company, country, region)
    context = dict()

    trip = get_object_or_404(Trip, slug=url)

    ratings = Rating.objects.filter(trip=trip).order_by("-date_created")
    
    recommendations = 0
    counter = 0
    
    for rating in ratings:
        counter += 1
        if rating.nps_indication > 3:
            recommendations += 1
            
    if counter > 0:
        context['recommendation_rate'] = (recommendations / counter) * 100

    overall_ratings = dict()

    for field in Rating._meta.get_fields():

        if field.get_internal_type() == "IntegerField" or field.get_internal_type() == "DecimalField":

            overall_ratings[field.name] = ratings.aggregate(Avg(field.name))['{}__avg'.format(field.name)]

        elif field.get_internal_type() == "BooleanField":

            if ratings.count() > 0:
                overall_ratings[field.name] = ratings.aggregate(**{
                    field.name: Count(Case(When(then=1, **{field.name: True})))
                })[field.name]

    if overall_ratings['overall_rating'] != trip.overall_rating or trip.rating_count != ratings.count():
        trip.overall_rating = overall_ratings['overall_rating']
        trip.rating_count = ratings.count()
        trip.save()

    template = 'travelling/trips/trip-detail-page.html'

    context['object'] = trip

    try:
        context['profile'] = CorporateProfile.objects.get(company_name=trip.company)
    except CorporateProfile.DoesNotExist or AttributeError or IndexError:
        pass

    context['ratings'] = ratings
    context['overall_rating'] = overall_ratings

    context['hunter_data'] = modelformset_factory(HunterDataInInquiry, AddHunterToInquiryForm, extra=5)

    try:
        context['company'] = CorporateProfile.objects.get(pk=trip.company.pk)

    except CorporateProfile.DoesNotExist:
        pass

    if request.user.is_authenticated:
        try:
            context['inquiry'] = TripInquiry.objects.get(trip=trip, user=request.user)
        except TripInquiry.DoesNotExist:
            pass

    context['reply_to_rating_form'] = ReplyToRatingForm
    context['price_list'] = render_price_list(trip)

    return render(request, context=context, template_name=template)


@login_required
def request_trip_deletion(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)

    profile = get_object_or_404(CorporateProfile, admin=request.user)

    trip.marked_for_deletion = True
    trip.save()

    mail_template = 'email/travelling/request-to-delete-trip.html'
    ctx = {
        'profile': profile,
        'trip': trip,
        'date': datetime.now(),
        'request': request
    }
    
    send_complex_mail(subject=_('{} requests to delete a trip.'.format(profile.company_name.name)),
                      html_template=mail_template, context=ctx, recipients=['brieftaube@jagdreisencheck.de'])

    return HttpResponseRedirect(reverse('travelling:modify_trip', args=(company, country, region)))


@login_required
def revise_trip_deletion(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)

    profile = get_object_or_404(CorporateProfile, admin=request.user)

    trip.marked_for_deletion = False
    trip.save()
    
    ctx = {
        'profile': profile,
        'trip': trip,
        'date': datetime.now(),
        'request': request
    }

    mail_template = 'email/travelling/revise-trip-deletion-order.html'
    send_complex_mail(subject=_('{} revises the deletion request a trip.'.format(profile.company_name.name)),
                      html_template=mail_template, context=ctx, recipients=['brieftaube@jagdreisencheck.de'])

    return HttpResponseRedirect(reverse('travelling:modify_trip', args=(company, country, region)))


@user_passes_test(lambda u: u.is_staff)
def delete_a_trip(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)
    msg = _('The Trip %s has been removed successfully.' % trip.name)
    trip.delete()

    messages.success(request, message=msg)
    return HttpResponseRedirect(reverse('jet-dashboard:moderate_trips'))


@user_passes_test(lambda u: u.is_staff)
def approve_trip(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)
    msg = _('The Trip %(region)s, %(country)s by %(company)s has been approved.' % {
        'region': trip.region,
        'country': trip.country.name,
        'company': trip.company.name
    })
    trip.is_approved = True
    trip.approval_date = datetime.now()
    trip.save()

    messages.success(request, message=msg)
    return HttpResponseRedirect(reverse('jet-dashboard:moderate_trips'))


@login_required
def create_game_instance(request):
    if request.method == 'POST' and request.is_ajax():
        form = CreateGameForm(request.POST)

        try:
            Game.objects.get(name=request.POST.get('name'))
            return JsonResponse(data={
                'errors': {
                    'name': _('Game already exisits!')
                },
                'value': Game.objects.get(name=request.POST.get('name')).pk
            })

        except IntegrityError:
            pass

        except Game.DoesNotExist:
            if form.is_valid():
                form = form.save(commit=False)
                form.created_by = request.user
                form.save()

                game = model_to_dict(form)
                game['pk'] = form.pk

                return JsonResponse(data={
                    'msg': _('Game created successfully.'),
                    'game': game,
                })

            else:
                return JsonResponse(data={
                    'msg': _('Error while creating game.'),
                    'errors': form.errors
                })
    else:
        return JsonResponse(data={'msg': _('Forbidden request.')})


@login_required_with_params
def rate_trip(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)

    try:
        Rating.objects.get(trip=trip, user=request.user)

        messages.error(request=request,
                       message=_('You have already posted a rating. Multiple ratings are not allowed.'),
                       extra_tags='danger')
        return HttpResponseRedirect(reverse('travelling:show_trip', args=(company, country, region)))
    except Rating.DoesNotExist:
        pass

    if request.user.is_company:
        messages.error(request=request, message=_('As you are corporate you are not allowed to rate.'),
                       extra_tags='danger')
        return HttpResponseRedirect(reverse('travelling:show_trip', args=(company, slugify(country), region)))

    template = 'travelling/rating/trip-rating-base-form.html'

    context = {
        'object': trip,
        'form': TripRatingForm,
    }

    try:
        context['company'] = CorporateProfile.objects.get(pk=trip.company.pk)
    except CorporateProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = TripRatingForm(request.POST)
        context['form'] = TripRatingForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.trip = trip
            form.user = request.user
            form.language = request.path.split(sep='/')[1]

            eco_rating = form.professional_hunter_quality + form.organization_of_hunt
            rating_count = 5

            if form.hunt_in_wilderness is False:
                eco_rating += 1
            else:
                eco_rating += 5

            if form.check_strike_pos is False:
                eco_rating += 1
            else:
                eco_rating += 5

            if form.check_hunt_license is False:
                eco_rating += 1
            else:
                eco_rating += 5

            if form.use_of_dogs is True:
                eco_rating += form.dog_quality
                rating_count += 1
            if form.game_density is not 0:
                eco_rating += form.game_density
                rating_count += 1
            if form.game_age_dist is not 0:
                eco_rating += form.game_age_dist
                rating_count += 1
            if form.game_gender_dist is not 0:
                eco_rating += form.game_gender_dist
                rating_count += 1

            form.ecologic_rating = eco_rating / rating_count

            social_rating = form.customer_support + form.hunting_introduction + form.communication_quality + \
                            form.support_with_issues + form.price_utility
            rating_count = 5
            
            if form.accommodation_type != 'SO':
                social_rating += form.accommodation_rating
                rating_count += 1
                
            if form.meal_option != 'N':
                social_rating += form.meal_quality
                rating_count += 1

            if form.alternative_program is True:
                social_rating += form.quality_alternative_program
                rating_count += 1

            form.social_rating = social_rating / rating_count
            form.overall_rating = (form.social_rating + form.ecologic_rating) / 2

            form.save()

            messages.success(request=request, message=_('Thank you for your Rating!'))

            trip.overall_rating = Rating.objects.filter(trip=trip).aggregate(Avg('overall_rating'))[
                'overall_rating__avg']
            trip.rating_ecologic = Rating.objects.filter(trip=trip).aggregate(Avg('ecologic_rating'))[
                'ecologic_rating__avg']
            trip.rating_sociocultural = Rating.objects.filter(trip=trip).aggregate(Avg('social_rating'))[
                'social_rating__avg']
            trip.rating_count = Rating.objects.filter(trip=trip).count() + 1

            trip.save()

            ctx = {
                'user': request.user,
                'trip': trip,
                'rating': form,
                'date': datetime.now(),
                'request': request,
                'title': _('Your trip to %(region)s in %(country)s has got a new rating!'.format(
                    {'region': trip.region, 'country': trip.country.name})
                ),
            }

            to_mail = 'herbert.woisetschlaeger@jagdreisencheck.de'

            if not settings.DEBUG and not os.environ.get('testsystem', None) == 'True':
                try:
                    corporate_profile = CorporateProfile.objects.get(company_name=trip.company)
                    to_mail = corporate_profile.admin.email
                    ctx['user'] = corporate_profile
                except CorporateProfile.DoesNotExist:
                    pass
                
            send_complex_mail(subject=_('Your trip to %(region)s in %(country)s has got a new rating!'.format(
                {'region': trip.region, 'country': trip.country.name}),
                              recipients=[to_mail], context=ctx,
                              html_template='email/travelling/notify-operator-about-rating.html'))
            
            validate_referral(request.user.referral_code)

            return HttpResponseRedirect(reverse('travelling:show_trip', args=(company, slugify(country), region)))
        else:

            return render(request=request, context=context, template_name=template)

    return render(request=request, context=context, template_name=template)


@login_required
def update_trip_rating(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)
    rating = get_object_or_404(Rating.objects.filter(user=request.user), trip=trip)

    template = 'travelling/rating/update-rating-page.html'

    context = {
        'object': trip,
        'form': UpdateTripRatingForm(instance=rating),
        'update_view': True
    }

    try:
        context['company'] = CorporateProfile.objects.get(pk=trip.company.pk)
    except CorporateProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = UpdateTripRatingForm(request.POST, instance=rating)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request=request, message=_('Thank you for updating your review!'))
            
            return HttpResponseRedirect(reverse('travelling:show_trip', args=(company, slugify(country), region)))
        else:
            context['form'] = form
            return render(request=request, context=context, template_name=template)

    return render(request=request, context=context, template_name=template)


@login_required
def reply_to_rating(request):
    
    # TODO: FIX RATING REPLY

    if request.method == "POST":
        form = ReplyToRatingForm(request.POST)

        rating = get_object_or_404(Rating, pk=request.POST.get('rating', None))

        try:
            reply = RatingReply.objects.get(rating=rating)
            reply.text = request.POST.get('text')
            reply.save()
        except RatingReply.DoesNotExist:

            if form.is_valid():
                form = form.save(commit=False)
                form.rating = rating
                form.author = request.user
                form.trip = Trip.objects.get(pk=request.POST.get('trip', None))
                form.save()

        return HttpResponseRedirect(reverse('travelling:show_trip', args=(rating.trip.company.slug,
                                                                          slugify(rating.trip.country),
                                                                          slugify(rating.trip.region))))


@login_required
def corporate_list_of_trips(request):
    template = 'travelling/trips/corporate-list-of-all-trips.html'
    context = dict()

    try:
        company = CorporateProfile.objects.get(admin=request.user)
        inquiries = TripInquiry.objects.filter(trip__company=company.pk, read=False)
        trips = Trip.objects.filter(company=company.company_name).order_by('country')

        trip_list = list()

        for trip in trips:
            inq = inquiries.filter(trip=trip).count()

            trip_list.append({'trip': trip, 'inquiries': inq})

        context['objects'] = trip_list
        context['inquiries'] = inquiries
        context['company'] = company

        return render(request=request, context=context, template_name=template)

    except CorporateProfile.DoesNotExist:
        return HttpResponseRedirect(reverse('accounts:console'))


@login_required
def modify_trip(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)

    trip = get_object_or_404(Trip, slug=url)
    company = get_object_or_404(CorporateProfile, company_name=trip.company)

    if company.admin == request.user:
        template = 'travelling/trips/modifications/trip_modification/update-trip-details.html'
        context = {
            'form': UpdateATripForm(instance=trip),
            'game_form': CreateGameForm(),
            'object': trip,
        }

        if request.method == 'POST':
            form = UpdateATripForm(request.POST, request.FILES, instance=trip)
            if form.is_valid():
                f = form.save(commit=True)
                f.save()

                messages.success(request=request, message=_('Trip updated successfully!'))
                return HttpResponseRedirect(reverse('travelling:show_trip', args=(company.company_name.slug,
                                                                                  country, region)))
            else:
                context['form'] = form

        return render(request=request, context=context, template_name=template)

    else:
        messages.error(request=request, message=_('Invalid request.'))
        return HttpResponseRedirect("/")


# Plugin Views
def generate_carousel(instance):
    app = ''
    for app in apps.get_app_configs():
        if app.name == instance.application:
            app = app.name

    application = app
    model = apps.get_model(app_label='travelling', model_name=str(instance.model))

    if instance.selection_criteria and len(instance.selection_criteria) > 0:
        pass
    else:
        pass

    data = {
        'objects': model.objects.all()
    }

    return data


def render_top_trips(instance):
    data = dict()

    data['globalTop'] = Trip.objects.all().order_by('rating').order_by('country.name')[:instance.num_objects]
    data['economicTop'] = Trip.objects.all().order_by('economic_rating').order_by('country.name')[:instance.num_objects]
    data['ecologicTop'] = Trip.objects.all().order_by('ecologic_rating').order_by('country.name')[:instance.num_objects]
    data['socioCulturalTop'] = Trip.objects.all().order_by('ecologic_rating') \
                                   .order_by('country.name')[:instance.num_objects]

    return data


# Plugin support views
def return_options_for_rating(request):
    context = dict()
    queryset = []

    trips = None

    if request.GET.get("company"):
        queryset.append(Q(**{"company": request.GET.get("company")}))

        trips = Trip.objects.filter(company=request.GET.get("company"), is_approved=True)

        countries = dict()
        for trip in trips:
            if trip.country.code in countries.keys():
                pass
            else:
                countries[trip.country.code] = trip.country.name

        context['results'] = {
            'countries': countries
            }

    if request.GET.get("company") and request.GET.get("country"):
        queryset.append(Q(**{"country": request.GET.get("country")}))

        trips = trips.filter(country=request.GET.get("country"))

        regions = list()
        for trip in trips:
            if trip.region in regions:
                pass
            else:
                regions.append({'value': slugify(trip.region), 'text': trip.region})

        context['results']['regions'] = regions

    if request.GET.get("region"):

        for element in context['results']['regions']:
            if element['value'] == request.GET.get('region'):
                queryset.append(Q(**{"region": element['text']}))

        try:

            trip = Trip.objects.get(functools.reduce(operator.and_, queryset))
            url = reverse('travelling:rate_trip', args=(trip.company.slug, slugify(trip.country.code),
                                                        slugify(trip.region)))
            
            if request.GET.get('ref'):
                url += '?ref=rate_trip'

            return HttpResponseRedirect(url)
        except ValueError or IndexError:
            context['error'] = _("We couldn't find a trip that fits your request. Please contact your operator.")

    return JsonResponse(context)


# AJAX Functions
def align_headline_image(request):

    if request.method == 'POST' and request.is_ajax():

        position = request.POST.get('y', 0)

        if request.POST.get('trip'):
            trip = Trip.objects.get(pk=request.POST.get('trip'))
            trip.headline_image_position = position
            trip.save()

        elif request.POST.get('company'):
            profile = CorporateProfile.objects.get(pk=request.POST.get('company'))
            profile.headline_image_position = position
            profile.save()
        elif request.POST.get('user'):
            profile = CorporateProfile.objects.get(pk=request.POST.get('user'))
            profile.headline_image_position = position
            profile.save()
        else:
            return JsonResponse(data={'error': _('Error moving the image. Please try again later.')}, status=500)

        return JsonResponse(data={'success': _('Position changed successfully.'), 'value': position}, status=200)

@csrf_exempt
def rate_review(request):
    """
    This function allows users to rate their peers' trip reviews by either liking or disliking them. For each vote a +1
    is either given to the like or dislike bracket.
    :param request: Accepts a HTTP request.
    :return: Returns a JSON object containing a status and the number of dis-/likes.
    """
    if request.method == "POST" and request.is_ajax():
        
        review = get_object_or_404(Rating, pk=request.POST.get("target"))
        score = request.POST.get("direction")  # Is either up or down, adding +1 or -1 score.
        
        if review:
            if score == "up":
                review.likes += 1
                review.save()
    
            elif score == "down":
                review.dislikes += 1
                review.save()
            
            return JsonResponse(data={
                    'status': {'success': _('Thank you for your feedback!')},
                    'data': {'likes': review.likes, 'dislikes': review.dislikes}
                }
            )
        
        else:
            return JsonResponse(data={
                    'status': {'error': _('Invalid Request. No rating found!')}
                }
            )


################################################################################################
#                                             SITEMAPS                                         #
################################################################################################
class TripSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.95
    hreflang = ["de", "en"]
    i18n = True
    protocol = 'https'
    
    def location(self, obj):
        return reverse('travelling:show_trip', args=[obj.company.slug, slugify(obj.country.code), slugify(obj.region)])

    def items(self):
        return Trip.objects.all()

    def lastmod(self, obj):
        return obj.last_modified