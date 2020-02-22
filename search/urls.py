from django.conf.urls import url

from search.views import *


app_name = 'search'
urlpatterns = [
    url(r'^admin/fetch/model/fields/$', fetch_model_fields, name='fetch_model_fields'),
    url(r'^prefetch/$', prefetch_trips, name='prefetch_trips'),
    url(r'^([a-zA-Z0-9ÄÖÜäöüß\-\_\ ]+)/$', list_trips_per_country, name='country_list'),
    url(r'^$', retrieve_results, name='retrieve_search_results'),
    
]
