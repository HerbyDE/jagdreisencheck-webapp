from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.http.response import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required

from travelling.models import Trip
from accounts.models import CorporateProfile

from pricing.models import PriceList, PackageTour, Price, GamePrice, AccommodationPrice, OtherPrice
from pricing.forms import (HandlePriceListForm, HandlePackageTourForm, HandlePriceForm, HandleGamePriceForm,
                           HandleAccommodationPriceForm, HandleOtherPriceForm)


# Create your views here.
@user_passes_test(lambda u: u.is_company)
def price_list_overview(request, company, country, region):
    url = '/{}/{}/{}/'.format(company, country, region)
    trip = get_object_or_404(Trip, slug=url)
    
    price_lists = PriceList.objects.filter(trip=trip)
    
    ctx = {
        'price_lists': price_lists,
        'trip': trip
    }
    
    return render(request=request, template_name='pricing/company/price-list-overview.html', context=ctx)


@user_passes_test(lambda u: u.is_company)
def get_or_create_pricelist(request, company, country, region, p_list=None, package_tour=None):
    url = '/{}/{}/{}/'.format(company, country, region)
    
    trip = get_object_or_404(Trip, slug=url)
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    list_form = HandlePriceListForm()
    pack_form = HandlePackageTourForm()
    price_form = HandlePriceForm()
    game_form = HandleGamePriceForm()
    acco_form = HandleAccommodationPriceForm()
    other_form = HandleOtherPriceForm()
    
    other_form.fields['text'].choices = [(choice.text, choice.text) for
                                         choice in OtherPrice.objects.all().distinct()] + [('', _('Other'))]
    ctx = dict()
    
    if p_list:
        price_list = get_object_or_404(PriceList, pk=p_list)
        list_form = HandlePriceListForm(instance=price_list)
        ctx['price_list'] = price_list
        ctx['game_prices'] = GamePrice.objects.filter(price__price_list=price_list).order_by("game__name","price__cost")
        ctx['accommodation_prices'] = AccommodationPrice.objects.filter(price__price_list=price_list).order_by(
            "accommodation", "price__cost")
        ctx['other_prices'] = OtherPrice.objects.filter(price__price_list=price_list).order_by("text", "price__cost")
    else:
        price_list = None
    
    if request.GET.get('package-tour') or package_tour:
        try:
            package_tour = PriceList.objects.get(pk=package_tour)
            pack_form = HandlePackageTourForm(instance=package_tour)
            ctx['package_tour'] = package_tour

            ctx['game_prices'] = GamePrice.objects.filter(price__package_tour=package_tour).order_by("game__name",
                                                                                                     "price__cost")
            ctx['accommodation_prices'] = AccommodationPrice.objects.filter(price__package_tour=package_tour).order_by(
                "accommodation", "price__cost")
            ctx['other_prices'] = OtherPrice.objects.filter(price__package_tour=package_tour).order_by("text",
                                                                                                       "price__cost")
                   
        except PriceList.DoesNotExist:
            pass
        
        ctx['pack_form'] = pack_form
    
    if request.method == "POST":
        
        form_selector = request.POST.get('form', None)
        
        if not form_selector:
            return HttpResponse("Error", status=400)
        
        if form_selector == 'list':
            list_form.data = request.POST
            list_form.is_bound = True
            
            if list_form.is_valid():
                form = list_form.save(commit=False)
                form.trip = trip
                
                if form.is_active:
                    for pl in PriceList.objects.filter(trip=trip):
                        pl.is_active = False
                        pl.save()

                form.save()
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_price_list', args=[company, country, region,
                                                                                       form.pk]))
               
        elif form_selector == 'package':
            pack_form.data = request.POST
            pack_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if pack_form.is_valid():
                pack = pack_form.save(commit=False)
                pack.price_list = price_list
                pack.save()

                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_package_tour', args=[company, country, region,
                                                                                         price_list.pk, pack.pk]))
                
        elif form_selector == 'game':
            game_form.data = request.POST
            game_form.is_bound = True
            
            price_form.data = request.POST
            price_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if game_form.is_valid() and price_form.is_valid():
                game = game_form.save(commit=False)
                price = price_form.save(commit=False)
                
                if package_tour:
                    price.package_tour = package_tour
                else:
                    price.price_list = price_list
                price.save()
                
                game.price = price
                game.save()

                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_price_list', args=[company, country, region,
                                                                                       price_list.pk]))
            
        elif form_selector == 'accommodation':
            acco_form.data = request.POST
            acco_form.is_bound = True
    
            price_form.data = request.POST
            price_form.is_bound = True
    
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
    
            if acco_form.is_valid() and price_form.is_valid():
                acco = acco_form.save(commit=False)
                price = price_form.save(commit=False)
                
                if package_tour:
                    price.package_tour = package_tour
                else:
                    price.price_list = price_list
                
                price.save()
        
                acco.price = price
                acco.save()
        
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_price_list', args=[company, country, region,
                                                                                       price_list.pk]))
        
        elif form_selector == 'other':
            other_form.data = request.POST
            other_form.is_bound = True
    
            price_form.data = request.POST
            price_form.is_bound = True
    
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
    
            if other_form.is_valid() and price_form.is_valid():
                other = other_form.save(commit=False)
                
                if other.text == 'O':
                    other.text = request.POST.get('other_text')
                
                price = price_form.save(commit=False)
                
                if package_tour:
                    price.package_tour = package_tour
                else:
                    price.price_list = price_list
                
                price.save()
        
                other.price = price
                other.save()
        
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_price_list', args=[company, country, region,
                                                                                       price_list.pk]))
        
    ctx.update({
        'list_form': list_form,
        'price_form': price_form,
        'game_form': game_form,
        'acco_form': acco_form,
        'other_form': other_form,
        'trip': trip,
    })
    
    return render(request=request, template_name='pricing/company/price-list-form.html', context=ctx)


@user_passes_test(lambda u: u.is_company)
def get_or_create_package_tour(request, company, country, region, p_list, package_tour=None):
    url = '/{}/{}/{}/'.format(company, country, region)
    
    trip = get_object_or_404(Trip, slug=url)
    price_list = get_object_or_404(PriceList, pk=p_list)
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    pack_form = HandlePackageTourForm()
    price_form = HandlePriceForm()
    game_form = HandleGamePriceForm()
    acco_form = HandleAccommodationPriceForm()
    other_form = HandleOtherPriceForm()
    other_form.fields['text'].choices = other_form.fields['text'].choices = [(choice.text, choice.text) for choice in
                                                                             OtherPrice.objects.all().distinct()] + \
                                                                            [('', _('Other'))]
    
    ctx = dict()
    ctx['price_list'] = price_list
    ctx['pack_form'] = pack_form
    
    if package_tour:
        try:
            package_tour = PackageTour.objects.get(pk=package_tour)
            pack_form = HandlePackageTourForm(instance=package_tour)
            ctx['package_tour'] = package_tour
            
            ctx['game_prices'] = GamePrice.objects.filter(price__package_tour=package_tour).order_by("game__name",
                                                                                                     "price__cost")
            ctx['accommodation_prices'] = AccommodationPrice.objects.filter(price__package_tour=package_tour).order_by(
                "accommodation", "price__cost")
            ctx['other_prices'] = OtherPrice.objects.filter(price__package_tour=package_tour).order_by("text",
                                                                                                       "price__cost")
        
        except PackageTour.DoesNotExist:
            pass
        
        ctx['pack_form'] = pack_form
    
    if request.method == "POST":
        
        form_selector = request.POST.get('form', None)
        
        if not form_selector:
            return HttpResponse("Error", status=400)
        
        elif form_selector == 'package':
            pack_form.data = request.POST
            pack_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if pack_form.is_valid():
                pack = pack_form.save(commit=False)
                pack.price_list = price_list
                pack.save()
                
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_package_tour', args=[company, country, region,
                                                                                         price_list.pk, pack.pk]))
        
        elif form_selector == 'game':
            game_form.data = request.POST
            game_form.is_bound = True
            
            price_form.data = request.POST
            price_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if game_form.is_valid() and price_form.is_valid():
                game = game_form.save(commit=False)
                price = price_form.save(commit=False)
                price.package_tour = package_tour
                price.save()
                
                game.price = price
                game.save()
                
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_package_tour', args=[company, country, region,
                                                                                         price_list.pk,
                                                                                         package_tour.pk]))
        
        elif form_selector == 'accommodation':
            acco_form.data = request.POST
            acco_form.is_bound = True
            
            price_form.data = request.POST
            price_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if acco_form.is_valid() and price_form.is_valid():
                acco = acco_form.save(commit=False)
                price = price_form.save(commit=False)
                price.package_tour = package_tour
                
                price.save()
                
                acco.price = price
                acco.save()
                
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_package_tour', args=[company, country, region,
                                                                                         price_list.pk,
                                                                                         package_tour.pk]))
        
        elif form_selector == 'other':
            other_form.data = request.POST
            other_form.is_bound = True
            
            price_form.data = request.POST
            price_form.is_bound = True
            
            if not price_list:
                return HttpResponseRedirect(reverse('pricing:new_price_list'))
            
            if other_form.is_valid() and price_form.is_valid():
                other = other_form.save(commit=False)
                
                if other.text == 'O':
                    other.text = request.POST.get('other_text')
                
                price = price_form.save(commit=False)
                price.package_tour = package_tour
                
                price.save()
                
                other.price = price
                other.save()
                
                messages.success(request=request, message=_('Operation successful'))
                return HttpResponseRedirect(reverse('pricing:update_package_tour', args=[company, country, region,
                                                                                         price_list.pk,
                                                                                         package_tour.pk]))
                                                                                         
    ctx.update({
        'price_form': price_form,
        'game_form': game_form,
        'acco_form': acco_form,
        'other_form': other_form,
        'trip': trip,
    })
    
    return render(request=request, template_name='pricing/company/package-tour-form.html', context=ctx)


@user_passes_test(lambda u: u.is_company)
def remove_game_price(request, pk):
    game_price = get_object_or_404(GamePrice, pk=pk)
    trip = game_price.price.price_list.trip
    price_list = game_price.price.price_list
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    game_price.price.delete()
    
    messages.success(request=request, message=_('Object deleted successfully'))
    return HttpResponseRedirect(reverse('pricing:update_price_list',
                                        args=[trip.company.slug, slugify(trip.country.code), slugify(trip.region),
                                              price_list.pk]))


@user_passes_test(lambda u: u.is_company)
def remove_accommodation_price(request, pk):
    acco_price = get_object_or_404(AccommodationPrice, pk=pk)
    trip = acco_price.price.price_list.trip
    price_list = acco_price.price.price_list
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    acco_price.price.delete()
    
    messages.success(request=request, message=_('Object deleted successfully'))
    return HttpResponseRedirect(reverse('pricing:update_price_list',
                                        args=[trip.company.slug, slugify(trip.country.code), slugify(trip.region),
                                              price_list.pk]))


@user_passes_test(lambda u: u.is_company)
def remove_other_price(request, pk):
    other_price = get_object_or_404(OtherPrice, pk=pk)
    trip = other_price.price.price_list.trip
    price_list = other_price.price.price_list
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    other_price.price.delete()
    
    messages.success(request=request, message=_('Object deleted successfully'))
    return HttpResponseRedirect(reverse('pricing:update_price_list',
                                        args=[trip.company.slug, slugify(trip.country.code), slugify(trip.region),
                                              price_list.pk]))


@user_passes_test(lambda u: u.is_company)
def remove_package_tour(request, pk):
    package_tour = get_object_or_404(PackageTour, pk=pk)
    trip = package_tour.price_list.trip
    
    if not request.user == CorporateProfile.objects.get(company_name=trip.company).admin:
        return HttpResponseRedirect("/")
    
    package_tour.delete()
    
    messages.success(request=request, message=_('Object deleted successfully'))
    return HttpResponseRedirect(reverse('pricing:price_list_overview',
                                        args=(trip.company.slug, slugify(trip.country.code), slugify(trip.region))))


def render_price_list(trip):
    
    try:
        price_list = PriceList.objects.get(trip=trip, is_active=True)
        return price_list
    except PriceList.DoesNotExist:
        pass



