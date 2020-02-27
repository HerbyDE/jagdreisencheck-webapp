# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from travelling.views import (create_a_trip, retrieve_trip_details, create_game_instance, rate_trip, modify_trip,
                              return_options_for_rating, align_headline_image, reply_to_rating,
                              update_trip_rating, request_trip_deletion, revise_trip_deletion, delete_a_trip,
                              approve_trip, rate_review)


app_name = 'travelling'
urlpatterns = [

    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/update/rating/$', update_trip_rating, name='update_rating'),

    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/rate/$', rate_trip, name='rate_trip'),
    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/request/delete/$', request_trip_deletion,
        name='request_trip_deletion'),
    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/revise/delete/$', revise_trip_deletion,
        name='revise_trip_deletion'),
    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/admin/delete/$', delete_a_trip, name='delete_trip'),
    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/admin/approve/$', approve_trip, name='approve_trip'),
    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/modify/$', modify_trip, name='modify_trip'),

    url(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/$', retrieve_trip_details, name='show_trip'),

    url(r'^rating-choices/$', return_options_for_rating, name='rating_options'),

    url(r'^create/trip/$', create_a_trip, name='create_trip'),
    url(r'^create/game/$', create_game_instance, name='create_game_instance'),

    url(r'^update/trip/headline-image/$', align_headline_image, name='change_headline_y_position'),
    url(r'^reply/rating/$', reply_to_rating, name='reply_to_rating'),
    url(r'^rate_review/$', rate_review, name='rate_review'),
]
