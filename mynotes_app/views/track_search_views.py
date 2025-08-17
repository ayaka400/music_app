import requests
from django.http import JsonResponse
from project import settings
from django.shortcuts import render
from django.templatetags.static import static
import config.constants as const 

# 類似曲を取得する処理
def get_similar_tracks(track_name, artist_name):
    params = {
        'method': 'track.getSimilar',
        'artist': artist_name,
        'track': track_name,
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 5,
        'autocorrect': 1,
    }

    try:
        res = requests.get(const.API_URL, params=params)
        similar_data = res.json().get('similartracks', {}). get('track', [])
        similar_tracks = []

        for item in similar_data:

            # imageはget_track_info関数から取得
            image = get_track_info(track_name, artist_name).get('image') 
            similar_tracks.append({
                'name': item.get('name'),
                'artist': item.get('artist', {}).get('name', ''),
                'url': item.get('url', ''),
                'image': image,
            })

        return similar_tracks
    except Exception as e:
        print(f"[ERROR] get_similar_tracks: {e}")
        return []


# 楽曲詳細を取得する処理
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
        res = requests.get(const.API_URL, params=params)
        track = res.json().get('track', {})

        tags = [tag['name'] for tag in track.get('toptags', {}).get('tag', [])]
        wiki = track.get('wiki', {})

        image_list = track.get('album', {}).get('image', [])
        image_url = image_list[-1]['#text'] if image_list else ''
        image = image_url if image_url else const.DEFAULT_IMAGE

       # similar_tracks = get_similar_tracks(track_name, artist_name)

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
      #      'similar_tracks': similar_tracks,
        }
    except Exception as e:
        print(f"[ERROR] get_track_info: {e}")
        # 取得できなかった場合は引数で受け取った値のみ返す
        return {
            'name': track_name,
            'artist': artist_name,
            'mbid': mbid,
            'image': const.DEFAULT_IMAGE,
            'url': '',
            'playcount': '',
            'tags': [],
            'published': '',
            'summary': '',
            'content': '',
            'similar_tracks': [],
        }


# main処理

# 楽曲名から候補の楽曲情報一覧→楽曲詳細を表示する処理
def search_track(request):
    # GETリクエストからパラメーター(曲名)を抜きだしてqueryに格納
    query = request.GET.get('q', '')
    if not query:
        return render(request, "search_track.html", {"tracks": [], "query": ""})

    # 埋め込みたいパラメーターを辞書で作成
    params = {
        'method': 'track.search',
        'track': query, # GETリクエストに含まれていた曲名
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 5, # 上限指定
    }

    # URLにクエリパラメーターを埋め込んで送信
    response = requests.get(const.API_URL, params=params)

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

    return render(request, "search_track.html", {"tracks": tracks, "query": query})


# ある曲の詳細ページ表示
def track_detail_view(request):

    track_name = request.GET.get("track")
    artist_name = request.GET.get("artist")

    print(artist_name)

    track_info = get_track_info(track_name, artist_name)
    similar_tracks = get_similar_tracks(track_name, artist_name)

    return render(request, "track_detail.html", {
        "track": track_info,
        "similar_tracks": similar_tracks
    })
