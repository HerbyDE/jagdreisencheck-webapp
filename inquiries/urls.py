from django.conf.urls import re_path

from inquiries.views import create_inquiry, list_inquiries, mark_as_read, handle_inquiry_state


app_name = 'inquiries'
urlpatterns = [
    re_path(r'^([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/inquire/', create_inquiry, name='inquire_trip'),
    re_path(r'^inquiries/update/status/$', mark_as_read, name='update_inquiry'),
    re_path(r'^inquiries/change/([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/$', handle_inquiry_state,
            name='change_lead_status'),
    re_path(r'^inquiries/([a-zA-Z0-9\-\_]+)/([\w]{2})/([a-z0-9_\-]+)/$', list_inquiries, name='inquiry_list'),
    re_path(r'^inquiries/$', list_inquiries, name='inquiry_list'),
]