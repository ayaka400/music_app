from django.urls import path
from .views import track_search_views, artist_search_views

urlpatterns = [
    path('search_track/', track_search_views.search_track, name='search_track'),
    path('search_artist/', artist_search_views.search_artist, name='search_artist')
]
