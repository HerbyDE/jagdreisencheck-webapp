import json
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as li, logout as lo
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.signals import user_login_failed
from django.forms.models import model_to_dict
from django.db import IntegrityError, InternalError
from django.http import JsonResponse, Http404
from django.shortcuts import render, HttpResponseRedirect, reverse, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from django.contrib.sitemaps import Sitemap

from accounts.forms import (CreateBaseUserInstance, CreateIndividualProfileForm,
                            CreateCompanyNameInTripCreationForm, CreateCorporateProfileForm, ChangeProfilePictureForm,
                            ChangeProfileDescriptionForm, UpdateBaseUserInstance,
                            UpdateIndividualProfileForm, UpdatePrivacySettingsForm, ChangePasswordForm,
                            ResetPasswordByEmailForm, ResetPasswordByTokenForm, UpdateCorporateProfileContactForm,
                            UpdateCorporateProfileInformationForm, UpdateCompanyLogoForm, UpdateTravelInquiryForm)
from accounts.models import User, IndividualProfile, CompanyName, CorporateProfile, generate_short_uuid4
from jagdreisencheck.cryptography import (generate_password_reset_token, decode_password_reset_token)
from mailing.views import send_mail, validate_referral

from travelling.models import Trip, Rating
from inquiries.models import TripInquiry


# Create your views here.
def login(request):
    
    template_name = 'accounts/login/login-page.html'
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nxt = request.POST.get('next')
        
        if username and password:
            user = authenticate(request, email=username, password=password)
            if user is not None:
                
                if not user.is_active:
                    messages.error(request, _('Your Account is inactive!'), extra_tags='danger')
                    return HttpResponseRedirect(reverse('accounts:user_login'))
                else:
                    li(request, user)
                    if user.is_company:
                        nxt = reverse('accounts:console')
                    elif str(nxt) == str(reverse('accounts:user_login')):
                        nxt = '/'
                    
                    return HttpResponseRedirect(nxt)
                
            else:
                user_login_failed.send(
                    sender=User,
                    request=request,
                    credentials={
                        'email': username
                    },
                )
                messages.error(request, _('An account with these credential does not exist. Please try again or reset '
                                          'your password.'))
                return HttpResponseRedirect(reverse('accounts:user_login'))
    
    return render(request=request, context={}, template_name=template_name)


def logout(request):
    lo(request)
    return HttpResponseRedirect("/")


def register_user(request):
    
    if request.user.is_authenticated and not settings.DEBUG and not eval(os.environ['testsystem']):
        return HttpResponseRedirect("/")
    
    template = 'accounts/registration/user-registration/base.html'
    user_form = CreateBaseUserInstance
    profile_form = CreateIndividualProfileForm

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    if request.method == 'POST':
        uform = user_form(request.POST)
        pform = profile_form(request.POST, request.FILES)

        context = {
            'user_form': uform,
            'profile_form': pform
        }

        if uform.is_valid():
            if request.POST.get('password') == request.POST.get('confirm_passwd'):
                uform = uform.save(commit=False)
                uform.password = make_password(request.POST.get('password'))
                uform.is_company = False
                if pform.is_valid():
                    uform.save()
                    pform = pform.save(commit=False)
                    pform.id = uform.id
                    pform.user = User.objects.get(pk=uform.pk)
                    pform.save()
                    
                    ref_link = '{}{}{}{}{}'.format(reverse('accounts:validate_account'), '?token=',
                                                   uform.activation_key['token'].decode('utf-8'), '&email=',
                                                   uform.email)
                                                 
                    if request.POST.get('next'):
                        ref_link += '&next={}'.format(request.POST.get('next'))
                    
                    mctx = {
                        'headline': _('Welcome aboard!'),
                        'request': request,
                        'user': uform,
                        'token': uform.activation_key['token'].decode('utf-8'),
                        'link': ref_link
                    }
                    
                    html_template = 'accounts/registration/user-registration/sign-up-email.html'
                    
                    send_mail(subject=_('Verify your Account'), recipients=[uform.email], html_template=html_template,
                              context=mctx)
                    
                    uform.referral_code = uform.pk
                    uform.save()
                    if request.POST.get('referred_by'):
                        try:
                            user = User.objects.get(referral_code=request.POST.get('referred_by'))
                            uform.referred_by = user.referral_code
                            uform.save()
                        except User.DoesNotExist or IntegrityError or IndexError or User.MultipleObjectsReturned:
                            pass
                        
                    return HttpResponseRedirect(reverse('accounts:thankyou'))
                else:
                    uform.delete()
                    return render(request, template, context)
            else:
                uform.errors['password'] = _('The passwords do not match')
                context['user_form'] = uform
                return render(request, template, context)

    return render(request, template, context)


def check_username_email(request):
    email = False
    if request.GET.get('email'):
        email = request.GET.get('email')
        try:
            user = User.objects.get(email=email)
            email = False
        except User.DoesNotExist:
            email = True
    resp = json.dumps({'email': email})
    return JsonResponse(resp, safe=False)


def register_company(request):
    
    if request.user.is_authenticated and not settings.DEBUG and not eval(os.environ['testsystem']):
        return HttpResponseRedirect("/")

    template = 'accounts/registration/company-registration/base.html'
    user_form = CreateBaseUserInstance
    company_form = CreateCompanyNameInTripCreationForm
    profile_form = CreateCorporateProfileForm

    context = {
        'user_form': user_form,
        'company_form': company_form,
        'profile_form': profile_form
    }

    if request.method == 'POST':
        
        uform = user_form(request.POST)
        cform = company_form(request.POST)
        pform = profile_form(request.POST)

        context = {
            'user_form': uform,
            'company_form': cform,
            'profile_form': pform,
        }

        if uform.is_valid():
            if request.POST.get('password') == request.POST.get('confirm_passwd'):
                uform = uform.save(commit=False)
                uform.password = make_password(request.POST.get('password'))
                uform.is_company = True
                try:
                    uform.save()
                except IntegrityError or InternalError:
                    messages.error(request=request, message=_('The user already exists! Please try resetting your '
                                                              'password or drop us an e-mail'))
                    return render(request, template, context)

                try:
                    instance = CompanyName.objects.get(name__iexact=request.POST.get('name'))
                    company_name = CreateCompanyNameInTripCreationForm(request.POST, instance=instance)
                    
                    if instance.has_profile:
                        messages.error(request, message=_('This company already has a corporate profile. '
                                                          'If this is your company and you perceive an abuse contact us'
                                                          'immediately at info@jagdreisencheck.de.'))
                        return HttpResponseRedirect("/")
                    
                    if company_name.is_valid():
                        company_name = company_name.save(commit=False)
                        company_name.has_profile = True
                        company_name.save()
                    else:
                        messages.error(request, message=_('There is a problem with your data.'))
                        return render(request, template, context)
                    
                except CompanyName.DoesNotExist:
                    if cform.is_valid():
                        company_name = cform.save(commit=False)
                        company_name.id = uform.id
                        company_name.created_by = User.objects.get(id=uform.id)
                        company_name.has_profile = True
                        company_name.slug = slugify(company_name.name).replace("-", "_")
                        company_name.save()
                    else:
                        uform.delete()
                        return render(request, template, context)

                if pform.is_valid():
                    profile_form = pform.save(commit=False)
                    profile_form.id = uform.id
                    profile_form.company_name = company_name
                    profile_form.admin = uform
                    profile_form.save()

                    uform.company_name = company_name.name
                    uform.save()
                    
                    ref_link = '{}{}{}{}{}{}{}'.format(reverse('accounts:validate_account'), '?token=',
                                           uform.activation_key['token'].decode('utf-8'), '&email=',
                                           uform.email, '&next=', reverse('travelling:create_trip'))
                

                    mctx = {
                        'headline': _('Welcome aboard!'),
                        'request': request,
                        'user': uform,
                        'token': uform.activation_key['token'].decode('utf-8'),
                        'link': ref_link
                    }

                    html_template = 'accounts/registration/company-registration/sign-up-email.html'

                    send_mail(subject=_('Verify your Account'), recipients=[uform.email], html_template=html_template,
                              context=mctx)

                    messages.success(request=request,
                                     message=_('Thank you for registering! Please check your e-Mails.'))
                    return HttpResponseRedirect("{}{}".format(reverse('accounts:thankyou'), "?corporate"))
                else:
                    uform.delete()
                    company_name.has_profile = False
                    company_name.created_by = None
                    company_name.save()
                    return render(request, template, context)
            else:
                messages.error(request=request, message=_('The passwords do not match!'))
                uform.errors['password'] = _("The passwords do not match")
                return render(request, template, context)

    return render(request, template, context)


@login_required
def create_company_name_in_trip(request):
    if request.method == 'POST' and request.is_ajax():
        form = CreateCompanyNameInTripCreationForm(request.POST)

        try:
            CompanyName.objects.get(name__iexact=request.POST.get("name"))
            return JsonResponse(data={"msg": _("Company already exists!"), "errors": [_("Company already exists!")]})
        except CompanyName.DoesNotExist:
            pass

        if form.is_valid():
            form = form.save(commit=False)
            form.id = generate_short_uuid4()
            form.created_by = request.user
            form.has_profile = False
            form.slug = slugify(form.name).replace("-", "_")
            form.save()

            company = model_to_dict(form)
            company['pk'] = form.pk

            company = {
                'pk': form.pk,
                'name': form.name
            }

            return JsonResponse(data={
                'msg': _('Company created successfully.'),
                'company': company,
            })

        else:

            return JsonResponse(data={
                'msg': _('Error while creating company.'),
                'errors': form.errors
            })

    else:
        return JsonResponse(data={'msg': _('Forbidden request.')})


def profile_page(request, pk):
    context = dict()

    try:
        user = User.objects.get(pk=pk)
        
        if not request.user.is_authenticated:
            messages.error(request=request,
                           message=_('Login required! Hunter profiles may only be viewed when logged in.'))
            
            url = reverse('accounts:user_login')
            url = '{}{}{}'.format(url, '?next=', request.path)
            
            return HttpResponseRedirect(url)
        
    except User.DoesNotExist:
        try:
            user = CorporateProfile.objects.get(company_name__slug=pk)
        except CorporateProfile.DoesNotExist:
            raise Http404(_("Does not exist"))

    if user.company_name:
        trips = Trip.objects.filter(company=user.company_name)
        reviews = Rating.objects.filter(trip__company=user.company_name)

        rate_count = 0
        trip_count = 0

        for trip in trips:
            if type(trip.overall_rating).__name__ == 'NoneType':
                trip_overall_rating = 0
            else:
                trip_overall_rating = trip.overall_rating

            if trip_overall_rating > 0:
                rate_count += trip.overall_rating
                trip_count += 1

        trip_counter = trips.exclude(overall_rating__isnull=True).count()

        if trips.count() > 0 and trip_counter > 0:
            avg_company_rating = rate_count / trip_counter
        else:
            avg_company_rating = 0

        quick_facts = {'avg_company_rating': avg_company_rating}

        template = 'accounts/company/company-profile.html'
        context['object'] = user
        context['quick_facts'] = quick_facts
        context['reviews'] = reviews
        context['trips'] = trips

        if request.user.pk == user.pk:
            context['change_profile_pic_form'] = ChangeProfilePictureForm
            context['change_profile_descr_form'] = ChangeProfileDescriptionForm

    else:
        profile = IndividualProfile.objects.get(pk=pk)
        reviews = Rating.objects.filter(user=profile.user)

        template = 'accounts/user/user-profile.html'

        context['object'] = profile
        context['reviews'] = reviews

    return render(request, template, context)


class UpdateProfileView(View):
    '''
    This function handles all user profile updates and manages the required forms.
    Allowed methods are GET and POST. The context is parsed as objects (according to django good practice) and the
    actual identifier name. Required methods are ´get` and `post´.
    @:return Configured view that is capable of handling all profile updates.
    '''
    http_method_names = ['get', 'post']
    login_required = True

    def _get_model(self):
        try:
            profile = IndividualProfile.objects.get(pk=self.request.user.pk)
        except IndividualProfile.DoesNotExist:
            profile = CorporateProfile.objects.get(pk=self.request.user.pk)
        except CorporateProfile.DoesNotExist:
            return HttpResponseRedirect("/")

        return profile

    def _get_forms(self):
        forms = dict()
        forms['base_form'] = UpdateBaseUserInstance(instance=self.request.user)
        forms['password_form'] = ChangePasswordForm()
        if self.request.user.is_company:
            forms['profile_contact_form'] = UpdateCorporateProfileContactForm(instance=self._get_model())
            forms['profile_info_form'] = UpdateCorporateProfileInformationForm(instance=self._get_model())
            forms['profile_logo_form'] = UpdateCompanyLogoForm(instance=self._get_model().company_name)
        else:
            forms['profile_form'] = UpdateIndividualProfileForm(instance=self._get_model())
            forms['profile_info_form'] = UpdatePrivacySettingsForm(instance=self._get_model())

        return forms

    def get_context_data(self):
        context = dict()
        context['object'] = self._get_model()
        context['profile'] = self._get_model()
        context.update(self._get_forms())

        return context

    def _get_template(self):
        if self.request.user.is_company:
            template_name = 'accounts/company/settings/corporate-settings.html'
        else:
            template_name = 'accounts/user/settings/individual-settings.html'

        return template_name

    def get(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            messages.error(request=request, message=_('Forbidden request.'))
            return HttpResponseRedirect("/")

        return render(request=self.request, context=self.get_context_data(), template_name=self._get_template())

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(request=request, message=_('Forbidden request.'))
            return HttpResponseRedirect("/")

        if not self.request.POST.get('form-name'):
            return self.get(self.request)
        
        context = self.get_context_data()

        form_name = self.request.POST.get('form-name')

        if form_name == 'base-user':
            request = self.request.POST.copy()
            request['email'] = self.request.user.email
            form = UpdateBaseUserInstance(request, instance=self.request.user)
            if form.is_valid():
                form = form.save(commit=False)
                form.save()
                messages.success(request=self.request, message=_("User data updated successfully."))
            else:
                context.update({'base_form': form})
                return render(self.request, self._get_template(), context)

        elif form_name == 'public-settings':
            form = UpdateIndividualProfileForm(request.POST, files=self.request.FILES, instance=self._get_model())
            if form.is_valid():
                form = form.save(commit=False)
                form.save()
                messages.success(request=self.request, message=_("Profile data updated successfully."))
            else:
                context.update({'profile_form': form})
                return render(self.request, self._get_template(), context)

        elif form_name == 'corporate-contact':
            form = UpdateCorporateProfileContactForm(data=request.POST, files=self.request.FILES, instance=self._get_model())

            if form.is_valid():
                form = form.save(commit=False)
                form.save()
                messages.success(request=request, message=_("Contact information changed successfully."))
            else:
                context.update({'profile_contact_form': form})
                return render(self.request, self._get_template(), context)

        elif form_name == 'corporate-profile':
            
            data = self.request.POST.copy()
            
            data['operator_type'] = self._get_model().operator_type
            
            form = UpdateCorporateProfileInformationForm(data, request.FILES, instance=self._get_model())
            form2 = UpdateCompanyLogoForm(request.POST, request.FILES, instance=self._get_model().company_name)
            
            if form.is_valid() and form2.is_valid():
                form = form.save(commit=False)
                form.save()
                form2.save()
                messages.success(request=request, message=_("Profile information updated successfully."))
            else:
                context.update({'profile_info_form': form})
                return render(self.request, self._get_template(), context)

        elif form_name == 'privacy-settings':
            form = UpdatePrivacySettingsForm(self.request.POST, files=self.request.FILES, instance=self._get_model())
            if form.is_valid():
                form = form.save(commit=False)
                form.save()
                messages.success(request=self.request, message=_("Privacy settings updated successfully."))
            else:
                context.update({'profile_info_form': form})
                return render(self.request, self._get_template(), context)

        elif form_name == 'password-settings':
            form = ChangePasswordForm(request.POST, instance=self.request.user)
            old_password = self.request.user.password

            if form.is_valid():
                user = self.request.user
                user.password = make_password(request.POST.get('password'))
                user.save()
                messages.success(request=request, message=_("Password changed successfully."))
                return HttpResponseRedirect('/')
            
            context.update({'profile_info_form': form})
            return render(self.request, self._get_template(), context)

        return self.get(self.request)


@login_required
def request_saved_user_data(request):
    pass


def reset_password(request):
    template = 'accounts/reset/enter-email.html'
    context = dict()

    context['form'] = ResetPasswordByEmailForm()

    if request.method == 'GET':
        if request.GET.get('token'):
            template = 'accounts/reset/password.html'

            context['form'] = ResetPasswordByTokenForm()
            context['token'] = decode_password_reset_token(request, request.GET.get('token'))

        return render(request=request, context=context, template_name=template)

    elif request.method == 'POST':

        if request.POST.get('token'):
            try:
                token = {'status': 1, 'token': bytes(request.POST.get('token'), encoding='UTF-8')}
                user = User.objects.get(reset_token=token)
                if request.POST.get('password') == request.POST.get('confirm_password'):

                    form = ResetPasswordByTokenForm(request.POST, instance=user)
                    if form.is_valid():
                        form = form.save(commit=False)
                        form.reset_token = None
                        form.password = make_password(request.POST.get('password'))
                        form.save()

                        messages.success(request=request, message=_('Reset successful! Your password has been reset.'))

                    else:
                        messages.error(request=request, message=_('The provided data was wrong. Please retry.'))
                        return render(request=request, context=context, template_name=template)
                else:
                    context['token'] = request.POST.get('token')
                    messages.error(request=request, message=_('The passwords do not match.'))
                    url = u'{}?token={}'.format(reverse('accounts:reset_password'), request.POST.get('token'))
                    return HttpResponseRedirect(url)

            except User.DoesNotExist:
                messages.error(request=request, message=_('Invalid token.'))

            return HttpResponseRedirect(reverse('accounts:user_login'))

        else:

            try:
                form = ResetPasswordByEmailForm(request.POST, instance=User.objects.get(email=request.POST.get('email')))

                if form.is_valid():

                    user = User.objects.get(email=request.POST.get('email'))
                    user.reset_token = generate_password_reset_token(request, user)

                    user.save()

                    html_template = 'email/accounts/reset/password.html'
                    mail_ctx = {
                        'token': user.reset_token['token'].decode("utf-8"),
                        'request': request,
                        'user': request.user
                    }

                    send_mail(subject=_('Your password reset inquiry'), html_template=html_template, context=mail_ctx,
                              recipients=[user.email])

                    messages.success(request=request, message=_('Reset successful! Please check your e-mails.'))

                    return HttpResponseRedirect("/")

            except User.DoesNotExist:
                messages.error(request=request, message=_('This account does not exist.'))

                return HttpResponseRedirect("/")

            else:

                context['form'] = form
                messages.error(request=request, message=_('The provided data is invalid. Please retry.'))

    return render(request=request, context=context, template_name=template)


def check_validation_token(request):
    
    email = request.GET.get("email", None)
    token = request.GET.get("token", None)
    
    if not email or not token:
        messages.error(request=request, message=_('Missing data. Please check your token and email.'))
        return HttpResponseRedirect("/")
    
    try:
        user = User.objects.get(email=email)
        
        if user.is_active:
            messages.info(request=request, message=_('Your account is already active! You may reset you password.'))
            return HttpResponseRedirect(reverse('accounts:user_login'))
            
        if eval(user.activation_key)['token'].decode('utf-8') != token:
            messages.error(request=request, message=_('Invalid token! Please try again or contact us.'))
            return HttpResponseRedirect("/")
        
        user.is_active = True
        user.save()
        
        return user
        
    except User.DoesNotExist:
        return HttpResponseRedirect("/")
    

def validate_account(request):
    
    # Error handling is done in the token validator. The function returns a user.
    user = check_validation_token(request)
    
    if user.__class__.__name__ != 'User':
        return user

    mctx = {
        'user': user,
        'request': request,
        'headline': _('Your registration was successful!')
    }

    html_template = 'accounts/registration/verification-and-welcome-with-referral-email.html'
    
    if user.is_company:
        messages.success(request=request, message=_('Your account is now active.'))
        mctx['corporate'] = True
        mctx['link'] = '{}{}{}'.format(reverse('accounts:user_login'), '?next=', reverse('travelling:create_trip'))
    else:
        messages.success(request=request,
                         message=_('Your account is now active. Please check you inbox for confirmation.'))
        if request.GET.get('next'):
            mctx['link'] = '{}{}{}'.format(reverse('accounts:user_login'), '?next=', request.GET.get('next'))
        else:
            mctx['link'] = '{}'.format(reverse('accounts:user_login'))
            
        ref = ''
        
        if request.is_secure():
            ref += 'https://'
        else:
            ref += 'http://'
            
        ref += '{}'.format(request.get_host())
        
        mctx['ref_link'] = '{}{}{}{}'.format(ref, reverse('accounts:register'), '?referred_by=', user.referral_code)
        
    send_mail(subject=_('Verification successful!'), recipients=[user.email], html_template=html_template, context=mctx)
    
    validate_referral(user.referred_by)
    
    if request.GET.get('next', None):
        return HttpResponseRedirect(request.GET.get('next'))
    
    return HttpResponseRedirect(reverse('accounts:user_login'))


@login_required
@user_passes_test(lambda u: u.is_company)
def user_cockpit(request):
    template = 'accounts/company/company-cockpit.html'

    inquiries = TripInquiry.objects.filter(
        trip__company=CorporateProfile.objects.get(admin=request.user.pk).company_name, read=False).count()

    context = {
        'object': get_object_or_404(CorporateProfile, admin=request.user),
        'inquiries': inquiries
    }

    if request.user.is_company:
        return render(request=request, context=context, template_name=template)
    else:
        return HttpResponseRedirect("/")


@login_required
def inquiry_list(request, trip_pk=None):
    template = 'accounts/inquiries/inquiry-list.html'
    company = CorporateProfile.objects.get(admin=request.user.pk)
    inquiries = TripInquiry.objects.filter(trip__company=company.company_name).order_by('-date')

    if not company.has_lead_contract:
        messages.error(request=request, message=_('You need to have a subscription with us to use this functionality. '
                                                 'For further information please get in touch with us: '
                                                 'brieftaube@jagdreisencheck.de'))
        return HttpResponseRedirect(reverse('accounts:console'))

    if trip_pk:
        inquiries = inquiries.filter(trip=trip_pk)

    for inquiry in inquiries:
        inquiry.read = True
        inquiry.save()

    context = {
        'objects': inquiries,
        'form': UpdateTravelInquiryForm
    }

    return render(request=request, context=context, template_name=template)


@login_required
def user_list_of_inquiries(request, pk):
    template = 'accounts/user/list-of-inquiries.html'
    context = dict()

    if request.user.pk == pk:
        context['objects'] = TripInquiry.objects.filter(user=request.user).order_by("-date")

    return render(request, template, context)


@login_required
def update_inquiry(request):

    if request.method == 'POST':
        inquiry = get_object_or_404(TripInquiry, pk=request.POST.get('pk'))
        form = UpdateTravelInquiryForm(instance=inquiry, data=request.POST)

        if form.is_valid():
            form.save(commit=True)

            messages.success(request, message=_('Inquiry updated!'))

        else:

            messages.error(request, message=_('Error! Inquiry cannot be updated.'))

    return HttpResponseRedirect(reverse('accounts:inquiry_list'))


def thanks_for_registering(request):
    template = 'accounts/registration/thank-you.html'
    ctx = dict()
    
    if request.GET.get('corporate') != None:
        ctx['corporate'] = True

    return render(request, template, ctx)


@user_passes_test(lambda u: u.is_superuser)
def email_preview(request):
    template = 'accounts/registration/company-registration/sign-up-email.html'
    
    ctx = {
        'headline': _('Welcome aboard!'),
        'user': request.user,'link': '{}{}{}{}'.format(reverse('accounts:validate_account'), '?token=47337fho4173f14f714tf4-3184r4', '&next=', reverse('travelling:create_trip'))
    }
    
    return render(request=request, template_name=template, context=ctx)


################################################################################################
#                                             SITEMAPS                                         #
################################################################################################
class CorporateSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.85
    hreflang = ["de", "en"]
    i18n = True
    protocol = 'https'
    
    def location(self, obj):
        return reverse('accounts:user_profile', args=[obj.company_name.slug])
    
    def items(self):
        return CorporateProfile.objects.all()
    
    def lastmod(self, obj):
        return obj.last_modified