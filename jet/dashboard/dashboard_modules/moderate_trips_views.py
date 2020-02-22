from django.shortcuts import render, reverse, redirect, get_object_or_404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.contrib import messages
from django.template import loader
from django.contrib.auth.decorators import user_passes_test
from jet.dashboard import dashboard, forms

from travelling.models import Trip


@user_passes_test(lambda u: u.is_staff)
def moderate_trip(request):
    template = 'jet.dashboard/trip_moderation/trip-overview.html'
    context = dict()

    context['trips'] = Trip.objects.filter(is_approved=False)

    return render(request=request, template_name=template, context=context)


dashboard.urls.register_urls([
    url(r'^trips/moderate/$', moderate_trip, name='moderate_trips'),
])
