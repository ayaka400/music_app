import requests
from django.http import JsonResponse
from project import settings
from django.shortcuts import render
from django.templatetags.static import static

# 楽曲画像がなかった場合のデフォルト
DEFAULT_IMAGE = static('images/default.png')
# APIのRoot URL
API_URL  = 'http://ws.audioscrobbler.com/2.0/'

def get_track_info(track_name, artist_name, mbid=None):
    params = {
        'method': 'track.getInfo',
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'autocorrect': 1, # スペルミスを自動修正
        #'lang': 'ja',
    }

    if mbid:
        params['mbid'] = mbid
    else:
        params['track'] = track_name
        params['artist'] = artist_name

    try:
        res = requests.get(API_URL, params=params)
        track = res.json().get('track', {})

        tags = [tag['name'] for tag in track.get('toptags', {}).get('tag', [])]
        wiki = track.get('wiki', {})

        image_list = track.get('album', {}).get('image', [])
        image_url = image_list[-1]['#text'] if image_list else ''
        image = image_url if image_url else DEFAULT_IMAGE

        return {
            'name': track.get('name'),
            'artist': track.get('artist', {}).get('name', artist_name), # 'name'がなければ引数で受け取ったartist_nameを使う
            'mbid': track.get('mbid'),
            'image': image,
            'url': track.get('url'),
            'playcount': track.get('playcount'),
            'tags': tags,
            'published': wiki.get('published'),
            'summary': wiki.get('summary'),
            'content': wiki.get('content'),
        }
    except Exception as e:
        print(f"[ERROR] get_track_info: {e}")
        # 取得できなかった場合は引数で受け取った値のみ返す
        return {
            'name': track_name,
            'artist': artist_name,
            'mbid': mbid,
            'image': DEFAULT_IMAGE,
            'url': '',
            'playcount': '',
            'tags': [],
            'published': '',
            'summary': '',
            'content': '',
        }


def search_track(request):
    # GETリクエストからパラメーター(曲名)を抜きだしてqueryに格納
    query = request.GET.get('q', '')
    if not query:
        return render(request, "search_results.html", {"tracks": [], "query": ""})

    # 埋め込みたいパラメーターを辞書で作成
    params = {
        'method': 'track.search',
        'track': query, # GETリクエストに含まれていた曲名
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 10, # 上限指定
    }

    # URLにクエリパラメーターを埋め込んで送信
    response = requests.get(API_URL, params=params)

    # 応答結果をdataに格納
    data = response.json()

    #dataの中からtrackをキーとする値全体を格納
    raw_tracks = data.get('results', {}).get('trackmatches', {}).get('track', [])

    # 空のリストを作成
    tracks = []
    # 取得したtrackデータから必要な値を取得し変数に格納
    for track in raw_tracks:
        name = track.get('name')
        artist = track.get('artist')
        mbid = track.get('mbid') or None

        # 取得した値を引数としてget_track_infoに渡しレスポンスを格納
        detailed = get_track_info(name, artist, mbid)
        tracks.append(detailed)

    return render(request, "search_results.html", {"tracks": tracks, "query": query})
