import requests
from flask import Flask, redirect, Response

app = Flask(__name__)

# لیستی سێرڤەرە سەربەخۆکانی Piped/Invidious (بۆ ئەوەی ئەگەر یەکێکیان کاری نەکرد ئەوی تر کاربکات)
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.private.coffee",
    "https://pipedapi.lunar.icu",
    "https://piped-api.garudalinux.org"
]

def fetch_m3u8_from_piped(video_id):
    """رێگای پڕۆفێشناڵ: وەرگرتنی m3u8 لە ڕێگەی Piped API بۆ خۆدوورخستنەوە لە بلۆکی یوتوب"""
    for instance in PIPED_INSTANCES:
        try:
            url = f"{instance}/streams/{video_id}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # 1. پشکنینی لینکی m3u8 یان HLS لە ئەنجامەکەدا
                hls_url = data.get('hls')
                if hls_url:
                    return hls_url
                
                # 2. ئەگەر لە بەشی سەرەکی نەبوو، گەڕان لەناو بەشی streams
                for stream in data.get('streams', []):
                    if stream.get('format') == 'HLS' or stream.get('quality') == 'auto':
                        return stream.get('url')
        except Exception:
            continue
    return None

@app.route('/live/<video_id>')
def play_live(video_id):
    """کە لینکەکە دەکرێتەوە لە IPTV/VLC، ڕاستەوخۆ دەبڕێت بۆ لینکی m3u8"""
    m3u8_link = fetch_m3u8_from_piped(video_id)
    if m3u8_link:
        return redirect(m3u8_link, code=302)
    return "Error: Could not extract m3u8 stream", 404

@app.route('/playlist.m3u')
def generate_playlist():
    """فایلی M3U Playlist بۆ بەرنامەی IPTV"""
    host = Flask.request.host_url
    
    # ئایدی کەناڵ یان لایڤەکانت لێرە دابنێ
    channels = [
        {"name": "Live Channel 1", "id": "ijvDN4ex_BQ"}
    ]
    
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}", {ch["name"]}\n'
        m3u_content += f'{host}live/{ch["id"]}\n'
        
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
