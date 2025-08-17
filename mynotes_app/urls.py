from django.urls import path
from .views import track_search_views, artist_search_views, ranking_views

urlpatterns = [
    path('search_track/', track_search_views.search_track, name='search_track'),
    path('search_artist/', artist_search_views.search_artist, name='search_artist'),
    path('track/', track_search_views.track_detail_view, name='track_detail'),
    path('ranking/', ranking_views.top_track_views, name='ranking'),
]
