from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.http import JsonResponse
from django.template import loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import formset_factory, inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from inquiries.models import TripInquiry, Trip, HunterData
from inquiries.forms import TripInquiryForm, HunterDataForm, HunterDataFormset, ChangeInquiryStatusForm
from jagdreisencheck.decorators import login_required_with_params

from accounts.models import CorporateProfile


# Create your views here.
@login_required_with_params
@user_passes_test(lambda u: u.is_company is False)
def create_inquiry(request, company, country, region):
    
    url = '/{}/{}/{}/'.format(company, country, region)
    
    trip = get_object_or_404(Trip, slug=url)
    trip_form = TripInquiryForm()
    
    template = 'inquiries/user/inquire-trip-page.html'
    
    num = 0
    
    if request.GET.get('extraForms'):
        eva = eval(request.GET.get('extraForms'))
    
        if type(eva) == int and eva < 10:
            num = eva

    HunterDataForms = inlineformset_factory(parent_model=TripInquiry, model=HunterData, form=HunterDataForm, min_num=1,
                                            formset=HunterDataFormset, validate_min=num, extra=num, max_num=10)
    
    if request.method == 'POST':
        
        trip_form = TripInquiryForm(request.POST)
        
        if trip_form.is_valid():
            inquiry = trip_form.save(commit=False)
            inquiry.trip = trip
            inquiry.user = request.user
            
            HunterDataForms = HunterDataForms(request.POST, instance=inquiry)
            
            if HunterDataForms.is_valid():
                inquiry.save()
                HunterDataForms.save(commit=True)
                
                messages.success(request=request, message=_('Your inquiry has been submitted!'))
                return HttpResponseRedirect(reverse('travelling:show_trip', args=(company, country, region)))
        
    if request.is_ajax():
        forms = HunterDataForms().forms
        
        template_to_render = 'inquiries/user/inquire_trip_forms/hunter-data-ajax.html'
        render_ctx = {
            'hunter_forms': forms,
            'is_ajax': True,
            'trip': trip
        }
        
        res = loader.render_to_string(template_name=template_to_render, context=render_ctx, request=request)
        
        data = {
            'form': res
        }
        
        return JsonResponse(data=data)
            
    context = {
        'trip': trip,
        'form': trip_form,
        'hunter_data': HunterDataForms
    }
    
    return render(request=request, template_name=template, context=context)


@login_required
def list_inquiries(request, company=None, country=None, region=None):
    
    url = '/{}/{}/{}/'.format(company, country, region)
    context = dict()
    
    if request.user.is_company:
        
        corporate_profile = CorporateProfile.objects.get(admin=request.user)
        
        if not corporate_profile.has_lead_contract:
            messages.error(request=request, message=_('You are not allowed to access inquiries.'))
            return HttpResponseRedirect(reverse('accounts:console'))
        
        inquiries = TripInquiry.objects.filter(trip__company=CorporateProfile.objects.get(
            admin=request.user).company_name)
        
        if company and country and region:
            inquiries.filter(trip__slug=url)
        
        template = 'inquiries/company/inquiry-list.html'
        context['inquiries'] = inquiries
        
    else:
        template = 'inquiries/user/inquiry-list.html'
        context['inquiries'] = TripInquiry.objects.filter(user=request.user)
        
    return render(request=request, template_name=template, context=context)


@login_required
@user_passes_test(lambda u: u.is_company is True)
def mark_as_read(request):
    
    if request.is_ajax():
        inquiry = get_object_or_404(TripInquiry, iq=request.GET.get('iq', None))
        inquiry.read = True
        inquiry.save()
        
        return JsonResponse({'status': inquiry.read}, status=200)
    

@login_required
@user_passes_test(lambda u: u.is_company is True)
def handle_inquiry_state(request, company, country, region):
    
    if request.method == 'POST':
        url = '/{}/{}/{}/'.format(company, country, region)
        trip = get_object_or_404(Trip, slug=url)

        form = ChangeInquiryStatusForm(request.POST, instance=trip)
        
        if form.is_valid():
            form.save(commit=True)
            
        else:
            messages.error(request=request, message=_('There was an error updating your trip. Please try again later.'))

    return HttpResponseRedirect(reverse('accounts:console_trip_list'))
    
    


