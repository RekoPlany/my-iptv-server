import requests
import re
from flask import Flask, redirect, Response

app = Flask(__name__)

# لیستی APIیەکانی Invidious
INVIDIOUS_INSTANCES = [
    "https://inv.us.projectsegfau.lt",
    "https://invidious.nerdvpn.de",
    "https://invidious.drgns.space",
    "https://vid.mnp.gl"
]

def get_hls_url(video_id):
    # ڕێگای یەکەم: وەرگرتن لە ڕێگەی Invidious API
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1/videos/{video_id}"
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                hls_url = data.get('hlsUrl')
                if hls_url:
                    return hls_url
        except Exception:
            continue

    # ڕێگای دووەم (Backup): دەرهێنانی ڕاستەوخۆی hlsManifestUrl
    try:
        yt_page = requests.get(f"https://www.youtube.com/watch?v={video_id}", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }, timeout=4).text
        
        match = re.search(r'"hlsManifestUrl":"([^"]+)"', yt_page)
        if match:
            manifest_url = match.group(1).replace(r'\/', '/')
            return manifest_url
    except Exception:
        pass

    return None

@app.route('/live/<video_id>')
def play_live(video_id):
    m3u8_url = get_hls_url(video_id)
    if m3u8_url:
        return redirect(m3u8_url, code=302)
    return "Error: Could not extract m3u8 stream", 404

@app.route('/playlist.m3u')
def generate_playlist():
    host = Flask.request.host_url
    channels = [
        {"name": "Live Channel", "id": "ijvDN4ex_BQ"}
    ]
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}", {ch["name"]}\n'
        m3u_content += f'{host}live/{ch["id"]}\n'
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
