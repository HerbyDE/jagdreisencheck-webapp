# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url, include

from accounts.views import (profile_page, login, register_user, register_company, check_username_email, logout,
                            UpdateProfileView, create_company_name_in_trip, validate_account, user_cockpit,
                            reset_password, thanks_for_registering, user_list_of_inquiries, email_preview)
from travelling.views import corporate_list_of_trips

from seotools.views import render_registration_preamble

app_name = 'accounts'
urlpatterns = [
    url(r'^login/$', login, name='user_login'),
    url(r'logout/$', logout, name='user_logout'),
    # url(r'^api/', include('rest_framework.urls', namespace='rest_framework'), name='rest_framework'),
    url(r'^validate/ue/$', check_username_email, name='validate_ue'),
    url(r'^register/$', render_registration_preamble, name='register'),
    url(r'^register/user/$', register_user, name='register_user'),
    url(r'^register/thank-you/$', thanks_for_registering, name='thankyou'),
    url(r'^register/corporate/$', register_company, name='register_company'),
    url(r'^register/corporate/nameonly/$', create_company_name_in_trip, name='create_company_name'),
    url(r'^verify/$', validate_account, name='validate_account'),
    url(r'^console/$', user_cockpit, name='console'),
    url(r'^console/trips/list', corporate_list_of_trips, name='console_trip_list'),
    url(r'^reset/password/$', reset_password, name='reset_password'),
    url(r'email/preview/$', email_preview, name='email_preview'),
    # url(r'^(?P<pk>.+)/inquiries/$', user_list_of_inquiries, name='user_inquiries'),
    url(r'^(?P<pk>.+)/settings/$', UpdateProfileView.as_view(), name='settings'),
    url(r'^(?P<pk>.+)/$', profile_page, name='user_profile'),
]
