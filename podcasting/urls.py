from django.conf.urls import url
from podcasting.views import ShowListView, ShowDetailView, EpisodeListView, EpisodeDetailView


urlpatterns = [
    url(r"^podcasts/$", ShowListView.as_view(), name="podcasting_show_list"),
    url(r"^podcasts/(?P<slug>[-\w]+)/$", ShowDetailView.as_view(), name="podcasting_show_detail"),
    # url(r"^podcasts/(?P<show_slug>[-\w]+)/archive/$", EpisodeListView.as_view(), name="podcasting_episode_list"),
    # url(r"^(?P<show_slug>[-\w]+)/(?P<slug>[-\w]+)/$", EpisodeDetailView.as_view(), name="podcasting_episode_detail"),
]
