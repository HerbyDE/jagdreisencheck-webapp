from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from djangocms_blog.models import Post

from cms_plugin_directory.models import CardConfig, ContainerConfig, RowConfig, ColumnConfig, BlogThumbnailListConfig


class CMSBasePlugin(CMSPluginBase):
    module = _('Jagdreisencheck CMS Plugins')
    cache = True


class CMSContainer(CMSBasePlugin):
    model = ContainerConfig
    name = _('CMS Container')
    allow_children = True
    render_template = 'cms_plugin_templates/container/cms-container.html'


class CMSRow(CMSBasePlugin):
    model = RowConfig
    name = _('CMS Row')
    allow_children = True
    require_parent = True
    parent_classes = ['CMSContainer']
    render_template = 'cms_plugin_templates/row/cms-row.html'


class CMSColumn(CMSBasePlugin):
    model = ColumnConfig
    name = _('CMS Column')
    allow_children = True
    require_parent = True
    parent_classes = ['CMSRow']
    render_template = 'cms_plugin_templates/column/cms-column.html'


class CMSCard(CMSBasePlugin):
    model = CardConfig
    name = _('CMS Card')

    def get_render_template(self, context, instance, placeholder):
        return instance.template

    def render(self, context, instance, placeholder):
        context = super(CMSCard, self).render(context, instance, placeholder)

        return context
    
    
class BlogList(CMSBasePlugin):
    model = BlogThumbnailListConfig
    name = _('Blog Thumbnail List')
    render_template = 'cms_plugin_templates/blog_thumbnail_list/blog_thumbnail_list.html'
    
    def render(self, context, instance, placeholder):
        context = super(BlogList, self).render(context, instance, placeholder)

        context['objects'] = Post.objects.order_by('-date_published')[:instance.num_objects]
        
        return context
        

plugin_pool.register_plugin(CMSContainer)
plugin_pool.register_plugin(CMSRow)
plugin_pool.register_plugin(CMSColumn)
plugin_pool.register_plugin(CMSCard)
plugin_pool.register_plugin(BlogList)
