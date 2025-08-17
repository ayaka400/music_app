from django.shortcuts import render
import requests
from django.conf import settings
import config.constants as const
from .track_search_views import get_track_info

def top_track_views(request):
    country = request.GET.get('country', 'Japan') # デフォルトは日本
    mode = request.GET.get('mode', 'geo')

    if mode == 'geo':
        params = {
            'method': 'geo.getTopTracks',
            'country': country,
            'api_key': settings.LASTFM_API_KEY,
            'format': 'json',
            'limit': 10
        }
    else:
        params = {
            'method': 'chart.getTopTracks',
            'api_key': settings.LASTFM_API_KEY,
            'format': 'json',
            'limit': 10
        }

    try:
        res = requests.get(const.API_URL, params=params)
        if mode == 'geo':
            raw_tracks = res.json().get('toptracks', {}).get('track', [])
        else:
            raw_tracks = res.json().get('tracks', {}).get('track', [])

        tracks = []
        for t in raw_tracks:
            name = t.get('name')
            artist = t.get('artist', {}).get('name')
            mbid = t.get('mbid') or None
            detailed = get_track_info(name, artist, mbid) # カバー画像付き情報を取得
            tracks.append(detailed)

        return render(request, 'ranking.html', {
            'tracks': tracks,
            'country': country,
            'mode': mode
        })

    except Exception as e:
        print(f"[ERROR] top_tracks_view: {e}")
        return render(request, 'ranking.html', {
            'tracks': [],
            'country': country,
            'mode': mode
        })
