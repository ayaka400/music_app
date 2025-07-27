from django.urls import path
from .views import track_search_views

urlpatterns = [
    path('search/', track_search_views.search_track, name='search_track')
]
