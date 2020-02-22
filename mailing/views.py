from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import timedelta
from django.core.signing import TimestampSigner
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from accounts.models import User
from mailing.models import CustomerLoyaltyElement, MailingList, Mail
from travelling.models import Trip, Rating


# Create your views here.
def _send_mail(subject, recipients=None, text_body=None, html_template=None, context=None, attachments=None, cc=None, bcc=None):
    subject = subject

    if not type(recipients) == list and not type(cc) == list and not type(bcc) == list:
        return {'error': _('Invalid List of Recipients. Even one recipient needs to be passed in a list!')}

    if not text_body and not html_template:
        return {'error': _('Please either specify a text body or provide an html template with the respective context.')}

    if not context and html_template:
        return {'error': _('Please specify a context!')}

    if html_template:

        html_template = loader.get_template(html_template)
        html_template = html_template.render(context)

        msg = EmailMultiAlternatives(subject, html_template, settings.FROM_EMAIL)
        msg.content_subtype = "html"

        if text_body:
            text_body = loader.get_template(text_body)
            text_body = text_body.render(context)
            msg.attach_alternative(text_body, mimetype='text/plain')

    elif text_body:
        msg = EmailMultiAlternatives(subject, text_body, settings.FROM_EMAIL)

    else:
        return {'error': _('Invalid Data. Please either specify a text body or a html template with a context.')}

    if recipients and not cc and not bcc:
        msg.to = recipients

    if cc:
        msg.to = recipients | ['brieftaube@jagdreisencheck.de']
        msg.cc = cc

    if bcc:
        msg.to = ['brieftaube@jagdreisencheck.de']
        msg.bcc = bcc

    if attachments:
        if type(attachments) != list:
            return {'error': _('Invalid List of Attachments!')}

        for attachment in attachments:
            msg.attach_file(attachment)

    msg.send(fail_silently=True)
    return {'success': _('Mail sent successfully!')}


def send_mail(subject, recipients=None, text_body=None, html_template=None, context=None, attachments=None, cc=None, bcc=None):
    
    if settings.TESTSYSTEM:
        recipients = [settings.FROM_EMAIL]
    
    return _send_mail(subject, recipients, text_body, html_template, context, attachments, cc, bcc)


def send_mail_with_token(subject, recipients=None, text_body=None, html_template=None, context=None, attachments=None,
                         crypt_content=None, cc=None, bcc=None):
    if crypt_content and type(crypt_content) == dict:
        signer = TimestampSigner()
        context['token'] = signer.sign(crypt_content)

    if settings.TESTSYSTEM:
        recipients = [settings.FROM_EMAIL]

    return _send_mail(subject, recipients, text_body, html_template, context, attachments, cc, bcc)


def decrypt_token_mail(token):
    if token and type(token) == str:
        signer = TimestampSigner()
        return signer.unsign(token, max_age=timedelta(days=30))

    else:
        return {'error': _('Invalid Input at mail token decryption!')}
    
    
def check_for_customer_loyalty(user, element):

    if user.is_company:
        result = get_object_or_404(CustomerLoyaltyElement.objects.filter(corporate=True), pk=element)
    else:
        result = get_object_or_404(CustomerLoyaltyElement.objects.filter(corporate=False), pk=element)

    return result
    
    
def validate_referral(token):
    
    if not token:
        return False
    
    try:
        user = User.objects.get(referral_code=token)
        
        if not Rating.objects.filter(user=user).count() > 0 and User.objects.filter(referred_by=user.referral_code):
            file = check_for_customer_loyalty(user, 2)
            send_mail(subject=_('Jagdreisencheck check-list'), recipients=[user.email],
                      html_template='mailing/get-loyalty-element.html', context={'user': user},
                      attachments=[file.file.path])
            
        success = True
    except User.DoesNotExist:
        success = False
    
    return success


def unsubscribe(request):

    if request.GET.get('list') and request.GET.get('email'):
        mailinglist = get_object_or_404(MailingList, get_slug=request.GET.get('list'))
        mailinglist.subscribers.remove(User.objects.get(email=request.GET.get('email')))

        messages.success(request=request, message=_('You have been unsubscribed from the newsletter.'))
        return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/')


@user_passes_test(lambda u: u.is_superuser)
def render_mail(request):
    html_template = 'email/accounts/reset/password.html'
    mail_ctx = {
        'request': request,
        'user': request.user,
        'title': _('Welcome aboard!'),
        'trip': Trip.objects.all()[0]
    }

    return render(request, template_name=html_template, context=mail_ctx)

