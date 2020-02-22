from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from podcasting.models import Show


class PodcastOverview(CMSPluginBase):
    name = _('Podcast Show Overview')
    module = _('Blog')
    render_template = 'podcasting/plugins/show-list.html'

    def render(self, context, instance, placeholder):
        context = super(PodcastOverview, self).render(context, instance, placeholder)
        context['show_list'] = Show.objects.published()
        return context
    
    
plugin_pool.register_plugin(PodcastOverview)