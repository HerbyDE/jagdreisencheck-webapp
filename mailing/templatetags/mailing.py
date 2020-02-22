from django.shortcuts import get_object_or_404
from django import template

from mailing.models import CustomerLoyaltyElement
from accounts.models import CorporateProfile, CompanyName
from travelling.models import Trip, Rating

register = template.Library()


@register.inclusion_tag('mailing/get-loyalty-element.html', takes_context=True)
def render_loyalty_window(context, user):

    context['loyalty_elements'] = []

    if user.is_company:

        profile = get_object_or_404(CorporateProfile, admin=user)

        trips = Trip.objects.filter(company=profile.company_name)

        review_counter = 0

        for trip in trips:
            review_counter += Rating.objects.filter(trip=trip).count()

        if review_counter >= 30 or user.is_superuser:
            context['loyalty_elements'].append(CustomerLoyaltyElement.objects.get(pk=1))

    return context
