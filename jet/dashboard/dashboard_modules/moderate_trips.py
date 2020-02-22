# encoding: utf-8
import datetime
import json
from django import forms
from django.utils.translation import ugettext_lazy as _

from jet.dashboard.modules import DashboardModule
from jet.dashboard import dashboard

from travelling.models import Trip


class ModerateTripsModule(DashboardModule):
    title = _('Moderate Trips')
    template = 'jet.dashboard/modules/moderate-trips-overview.html'
    layout = 'stacked'
    children = []
    child_name = 'Trip'
    child_name_plural = 'Trips'

    def init_with_context(self, context):
        self.children = Trip.objects.filter(is_approved=False)[:10]
