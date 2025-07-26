import requests
from django.http import JsonResponse
from project import settings
from django.shortcuts import render

def search_track(request):
    # GETリクエストからパラメーター(曲名)を抜きだしてqueryに格納
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'No track name provided'}, status=400)
    # APIのRoot URL
    url = 'http://ws.audioscrobbler.com/2.0/'
    # 埋め込みたいパラメーターを辞書で作成
    params = {
        'method': 'track.search',
        'track': query, # GETリクエストに含まれていた曲名
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': 10, # 上限指定
    }

    # URLにクエリパラメーターを埋め込んで送信
    response = requests.get(url, params=params)

    # 応答結果をdataに格納
    data = response.json()
    print(data)    

    # dataから必要な情報だけ抽出
    tracks = data.get('results', {}).get('trackmatches', {}).get('track', [])
 
    # 空のリストを作成
    result = []
    # リストに各trackの辞書を入れていく
    for track in tracks:
        result.append({
            'name': track.get('name'),
            'artist': track.get('artist'),
            'mbid': track.get('mbid'),
            'image': track.get('image')[-1]['#text'] if track.get('image') else None
        })

   # return JsonResponse({'tracks': result}) # 'tracks' = キー = クライアントに返す文字列
    return render(request, "search_results.html", {"tracks": result , "query": query})
