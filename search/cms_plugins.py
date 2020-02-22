from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from search.models import SearchConfig
from search.views import generate_view


class SearchPlugin(CMSPluginBase):
    name = _('CMS Search Plugin')
    render_template = 'search/large_search_bar.html'
    cache = False

    def render(self, context, instance, placeholder):
        context = super(SearchPlugin, self).render(context, instance, placeholder)
        context['data'] = generate_view(context['request'])
        return context


plugin_pool.register_plugin(SearchPlugin)
