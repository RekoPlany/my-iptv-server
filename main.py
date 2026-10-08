import time
from flask import Flask, redirect, Response, render_template_string
import yt_dlp

app = Flask(__name__)

# کەشێک بۆ پاراستنی لینکەکان بۆ ماوەیەک تا سێرڤەرەکە بەبەردەوامی داواکاری نەنێرێت بۆ یوتوب
cache = {}
CACHE_TIME = 10800  # 3 کاتژمێر کات بۆ هەڵگرتنی لینکەکە

def extract_m3u8_url(youtube_url):
    """دەرهێنانی ڕاستەوخۆی لینکی m3u8 لە یوتوبەوە"""
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            # دانانی جۆری لینک
            m3u8_url = info.get('url')
            title = info.get('title', 'Live Stream')
            return m3u8_url, title
    except Exception as e:
        print(f"Error extracting stream: {e}")
        return None, None

def get_live_stream_cached(video_id):
    """پشکنینی هەبوونی لینکی هەڵگیراو لە حافظەی کاتیدا (Cache)"""
    current_time = time.time()
    
    # ئەگەر لینکەکە پێشتر هەبوو و بەسەر نەنچووبوو
    if video_id in cache:
        url, title, timestamp = cache[video_id]
        if current_time - timestamp < CACHE_TIME:
            return url, title
            
    # دروستکردنی لینکی نوێ ئەگەر لە حافظەدا نەبوو
    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    m3u8_url, title = extract_m3u8_url(yt_url)
    
    if m3u8_url:
        cache[video_id] = (m3u8_url, title, current_time)
        return m3u8_url, title
    return None, None

@app.route('/live/<video_id>')
def play_live(video_id):
    """کاتێک IPTV Player داوای کەناڵێک دەکات لە ڕێگەی Video ID"""
    m3u8_url, _ = get_live_stream_cached(video_id)
    if m3u8_url:
        return redirect(m3u8_url, code=302)
    return "نەتوانرا پەخشی ڕاستەوخۆ بەدەستبهێنرێت", 404

@app.route('/playlist.m3u')
def generate_playlist():
    """دروستکردنی فایلی IPTV Playlist بۆ ئەو لایڤانەی دەتەوێت"""
    # لیستی ڤیدیۆ/لایڤەکانی یوتوب (Video ID لە کۆتایی لینکەکە دەستدەکەوێت)
    CHANNELS = [
        {"name": "کەناڵی یەکەم", "id": "YOUR_VIDEO_ID_1"},
        {"name": "کەناڵی دووەم", "id": "YOUR_VIDEO_ID_2"},
    ]
    
    host = Flask.request.host_url
    m3u_content = "#EXTM3U\n"
    
    for ch in CHANNELS:
        m3u_content += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}", {ch["name"]}\n'
        m3u_content += f'{host}live/{ch["id"]}\n'
        
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
      
