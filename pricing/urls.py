from django.conf.urls import re_path

from pricing.views import (get_or_create_pricelist, price_list_overview, remove_game_price, remove_accommodation_price,
                           remove_other_price, get_or_create_package_tour, remove_package_tour)


app_name = 'pricing'
urlpatterns = [
    re_path(r'^([a-zA-Z0-9\-_]+)/([\w]{2})/([a-z0-9_\-]+)/preislisten/neu/$', get_or_create_pricelist,
            name='new_price_list'),
    re_path(r'^([a-zA-Z0-9\-_]+)/([\w]{2})/([a-z0-9_\-]+)/preislisten/([a-z0-9_\-]+)/$', get_or_create_pricelist,
            name='update_price_list'),
    re_path(r'^([a-zA-Z0-9\-_]+)/([\w]{2})/([a-z0-9_\-]+)/preislisten/([a-z0-9_\-]+)/pauschalangebot/$',
            get_or_create_package_tour, name='new_package_tour'),
    re_path(r'^([a-zA-Z0-9\-_]+)/([\w]{2})/([a-z0-9_\-]+)/preislisten/([a-z0-9_\-]+)/package-tour/([a-z0-9_\-]+)/$',
            get_or_create_package_tour, name='update_package_tour'),
    re_path(r'^([a-zA-Z0-9\-_]+)/([\w]{2})/([a-z0-9_\-]+)/preislisten/', price_list_overview,
            name='price_list_overview'),
    re_path(r'^remove/game/price/([0-9]+)/$', remove_game_price, name='remove_game_price'),
    re_path(r'^remove/accommodation/price/([0-9]+)/$', remove_accommodation_price, name='remove_accommodation_price'),
    re_path(r'^remove/other/price/([0-9]+)/$', remove_other_price, name='remove_other_price'),
    re_path(r'^remove/package-tour/([0-9]+)/$', remove_package_tour, name='remove_package_tour'),
]
