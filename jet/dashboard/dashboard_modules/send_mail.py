# encoding: utf-8
import datetime
import json
from django import forms
from django.utils.translation import ugettext_lazy as _

from jet.dashboard.modules import DashboardModule
from jet.dashboard import dashboard

from mailing.models import Mail


class SendMailItemForm(forms.Form):
    name = forms.TextInput()


class SendMailModule(DashboardModule):
    title = _('CRM E-Mails')
    template = 'jet.dashboard/modules/send-mass-mail-template.html'
    layout = 'stacked'
    children = []
    child_form = SendMailItemForm
    child_name = 'Mail'
    child_name_plural = 'Mails'

    def init_with_context(self, context):
        self.children = Mail.objects.filter(author=context.request.user).order_by('-date_created')[:5]


