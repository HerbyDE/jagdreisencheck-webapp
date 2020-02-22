from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.contrib import messages
from django.template import loader
from django.contrib.auth.decorators import user_passes_test
from jet.dashboard import dashboard, forms

from mailing.models import Mail, MailingList
from mailing.views import send_mail
from travelling.models import Trip


@user_passes_test(lambda u: u.is_staff)
def create_mail(request):
    template = 'jet.dashboard/modules/mailing-view.html'
    html_template = 'jet.dashboard/emails/email-template.html'
    context = dict()

    form = forms.SendMailForm

    if request.method == 'POST':
        form = forms.SendMailForm(request.POST)
        print(request.POST)

        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = request.user

            try:
                mlist = inst.target
                recipients = list()

                if inst.variant == 'IND':

                    for user in mlist.subscribers.all():
                        context = {
                            'email': inst,
                            'user': user,
                            'request': request
                        }
                        send_mail(subject=inst.title, html_template=html_template, context=context, recipients=[user.email])

                else:

                    for user in mlist.subscribers.all():
                        recipients.append(user.email)

                    context = {
                        'email': inst,
                        'request': request,
                        'user': None
                    }
                    send_mail(subject=inst.title, html_template=html_template, context=context, bcc=recipients)

                inst.sent = True

                inst.save()
                messages.success(request=request, message=_('Mail sent.'))
                return HttpResponseRedirect(reverse('admin:index'))

            except MailingList.DoesNotExist:
                messages.error(request=request, message=_('Mailing List does not exist.'))

    context['form'] = form

    return render(request=request, context=context, template_name=template)


def preview_mail(request, pk):

    ctx = {}
    template = 'jet.dashboard/emails/email-template.html'

    renderer_template = 'jet.dashboard/modules/mail-preview.html'
    renderer_context = {
        'email': get_object_or_404(Mail, pk=pk),
        'request': request,
        'user': request.user,
        'preview': True
    }

    tmp = loader.get_template(template)
    ctx['body'] = tmp.render(renderer_context)

    return render(request=request, context=ctx, template_name=renderer_template)


@user_passes_test(lambda u: u.is_staff)
def moderate_trip(request):
    template = 'jet.dashboard/trip_moderation/trip-overview.html'
    context = dict()

    context['trips'] = Trip.objects.filter(is_approved=False)
    context['request'] = request

    return render(request=request, template_name=template, context=context)


dashboard.urls.register_urls([
    url(r'^mail/send/$', create_mail, name='write_mail'),
    url(r'^mail/preview/(?P<pk>.+)/$', preview_mail, name='preview_mail'),
    url(r'^trips/moderate/$', moderate_trip, name='moderate_trips'),
])
