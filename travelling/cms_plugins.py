from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.shortcuts import HttpResponseRedirect, reverse

from travelling.models import Trip, TripCarouselConfig, TripBestOfModel, TripCatalogueModel
from travelling.views import generate_carousel, render_top_trips
from travelling.forms import FindATripToRateForm


class TripCarouselPlugin(CMSPluginBase):
    model = TripCarouselConfig
    name = _('Trip Carousel Plugin')
    module = _('Travel Platform')
    render_template = 'travelling/carousels/adaptive-slider.html'

    def render(self, context, instance, placeholder):
        context = super(TripCarouselPlugin, self).render(context, instance, placeholder)
        context['model'] = generate_carousel(instance)
        return context


class TripBestOfPlugin(CMSPluginBase):
    model = TripBestOfModel
    cache = True
    name = _('Trip Ranking Table')
    module = _('Travel Platform')
    render_template = 'travelling/best_of_lists/trip-best-of-list.html'

    def render(self, context, instance, placeholder):
        context = super(TripBestOfPlugin, self).render(context, instance, placeholder)
        context['objects'] = render_top_trips(instance)
        return context


class TripCatalogue(CMSPluginBase):
    model = TripCatalogueModel
    cache = True
    name = _('Trip Catalog')
    module = _('Travel Platform')
    render_template = 'travelling/trips/trip-list.html'

    def render(self, context, instance, placeholder):
        context = super(TripCatalogue, self).render(context, instance, placeholder)
        context['objects'] = Trip.objects.all()
        return context


class GuideToRatingPlugin(CMSPluginBase):
    cache = True
    login_required = True
    name = _('Find a trip to rate')
    module = _('Rating widgets')
    render_template = 'travelling/rating/guide-to-rating/guide.html'

    def render(self, context, instance, placeholder):
        context = super(GuideToRatingPlugin, self).render(context, instance, placeholder)
        context['form'] = FindATripToRateForm

        return context


class RenderKeyPlatformFacts(CMSPluginBase):
    cache = True
    login_required = False
    name = _('Show key facts of Jagdreisencheck')
    module = _('Rating widgets')
    render_template = 'travelling/plugins/show-rating-key-facts.html'


plugin_pool.register_plugin(TripCarouselPlugin)
plugin_pool.register_plugin(TripBestOfPlugin)
plugin_pool.register_plugin(TripCatalogue)
plugin_pool.register_plugin(GuideToRatingPlugin)
plugin_pool.register_plugin(RenderKeyPlatformFacts)
