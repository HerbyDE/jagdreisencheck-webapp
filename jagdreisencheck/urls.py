# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render_to_response
from django.views.static import serve

from travelling.views import TripSitemap
from accounts.views import CorporateSitemap

# Must be left here as the JET Dashboard would crash otherwise.
from jet.dashboard.dashboard_modules import google_analytics_views, send_mail_views


admin.autodiscover()
urlpatterns = [
    re_path(r'^sitemap\.xml', sitemap, {'sitemaps': {
        'cmspages': CMSSitemap,
        'trips': TripSitemap,
        'companies': CorporateSitemap
    }}),
    re_path(r'^robots\.txt', include('robots.urls')),
]

urlpatterns += i18n_patterns(
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^jet/', include('jet.urls', 'jet')),
    re_path(r'^jet/dashboard/', include('jet.dashboard.urls', namespace='jet-dashboard')),
    re_path(r'^admin/django-ses/', include('django_ses.urls')),
    re_path(r'^accounts/', include('accounts.urls', namespace='accounts'), name='accounts'),
    re_path(r'^accounts/', include('django.contrib.auth.urls'), name='auth'),
    re_path(r'^jagdreisen/', include('travelling.urls', namespace='travelling'), name='travelling'),
    re_path(r'^jagdreisen/', include('pricing.urls', namespace='pricing'), name='pricing'),
    re_path(r'^portal/', include('inquiries.urls'), name='inquires'),
    re_path(r'^jagdreisen/', include('search.urls', namespace='search'), name='search'),
    re_path(r'^comments/', include('django_comments.urls')),
    re_path(r'^slideshow/', include('slideshow.urls', namespace='slideshow'), name='slideshow'),
    re_path(r'^mailing/', include('mailing.urls', namespace='mailing'), name='mailing'),
    re_path(r'^news/', include('newsletter.urls'), name='newsletter'),
    re_path(r'^faq/', include('faq.urls'), name='faq'),
    re_path(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    re_path(r'^flat/', include('django.contrib.flatpages.urls')),
    re_path(r'^akademie/', include('podcasting.urls')),
    re_path(r'^akademie/', include('djangocms_blog.urls', namespace='Blog')),
    # re_path(r'^seo/', include('seotools.urls', namespace='seotools')),
    # re_path(r'^djangocms_comments/', include('djangocms_comments.urls')),
    re_path(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
      re_path('^media/(?P<path>.*)$', serve,
          {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ] + staticfiles_urlpatterns() + urlpatterns
    
    
def handler400(request, *args, **argv):
    return render_to_response(template_name='errorhandlers/400-Bad-Request.html', context={}, status=400)


def handler401(request, *args, **argv):
    return render_to_response(template_name='errorhandlers/401-Unauthorized.html', context={}, status=401)


def handler403(request, *args, **argv):
    return render_to_response(template_name='errorhandlers/403-Forbidden.html', context={}, status=403)


def handler404(request, *args, **argv):
    return render_to_response(template_name='errorhandlers/404-Not-Found.html', context={}, status=404)


def handler500(request, *args, **argv):
    return render_to_response(template_name='errorhandlers/500-Internal-Error.html', context={}, status=500)