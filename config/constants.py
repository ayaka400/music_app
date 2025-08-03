from django.templatetags.static import static

# Last.fm API のルートURL
API_URL = 'http://ws.audioscrobbler.com/2.0/'

# デフォルト画像（曲に画像がない場合）
DEFAULT_IMAGE = static('images/default.png')
