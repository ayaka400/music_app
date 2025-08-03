import requests
from django.shortcuts import render
from django.conf import settings
import config.constants as const
from .track_search_views import get_track_info


# アーティスト名からその代表曲(5曲)を取得する
def get_top_tracks(artist_name):
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 5,
        'autocorrect': 1,
    }

    try:
        res = requests.get(const.API_URL, params=params)
        tracks = res.json().get('toptracks', {}).get('track', [])

        result = []
        for track in tracks:
            track_name = track.get('name')
            url = track.get('url', '')

            # imageはget_track_info関数から取得           
            image = get_track_info(track_name, artist_name).get('image')

            result.append({
                'track_name': track_name,
                'image': image,
                'url': url,
            })

        return result

    except Exception as e:
        return []


# 検索ワードから該当アーティスト一覧を取得
def search_artist(request):
    query = request.GET.get('q', '')
    if not query:
        return render(request, "search_artist.html", {"artists": [], "query": ""})

    params = {
        'method': 'artist.search',
        'artist': query,
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 10,
        'autocorrect': 1,
    }

    response = requests.get(const.API_URL, params=params)
    data = response.json()

    # 検索ワードに該当するアーティスト一覧
    raw_artists = data.get('results', {}).get('artistmatches', {}).get('artist', [])
    artists = []

    for artist in raw_artists:
        name = artist.get('name')
        mbid = artist.get('mbid') or None
        url = artist.get('url', '')

        # 該当アーティストのトップ5曲を取得（関数呼び出し）
        top_tracks = get_top_tracks(name)

        artists.append({
            'name': name,
            'url': url,
            'top_tracks': top_tracks,
        })

    return render(request, "search_artist.html", {"artists": artists,"query": query})
