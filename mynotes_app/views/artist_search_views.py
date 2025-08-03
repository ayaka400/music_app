import requests
from django.shortcuts import render
from django.conf import settings
from django.templatetags.static import static
import config.constants as const

# 各アーティスト名からアーティスト詳細を取得
def get_artist_info(artist_name):
    params = {
        'method': 'artist.getInfo',
        'artist': artist_name,
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'autocorrect': 1,
    }

    try:
        res = requests.get(const.API_URL, params=params)
        data = res.json().get('artist', {})

        return {
            'name': data.get('name', artist_name),
            'url': data.get('url',  ''),
        }
    except Exception as e:
        print(f"[ERROR] get_artis_info: {e}")
        return {
            'name': artist_name,
            'url': '',
        }

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
    }

    response = requests.get(const.API_URL, params=params)
    data = response.json()

    raw_artists = data.get('results', {}).get('artistmatches', {}).get('artist', [])
    artists = []

    for artist in raw_artists:
        name = artist.get('name')
        detailed = get_artist_info(name) # アーティスト詳細情報取得関数を呼び出し
        artists.append(detailed)

    return render(request, "search_artist.html", {"artists": artists,"query": query})
