from django.conf.urls import url

from slideshow.views import handle_slideshow


app_name = 'slideshow'
urlpatterns = [
    url(r'^create/slideshow/$', handle_slideshow, name='create_slideshow'),
]