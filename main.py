import json
import re
import requests
from flask import Flask, redirect, Response

app = Flask(__name__)

def extract_m3u8_ios_client(video_id):
    """
    سەرکەوتووترین ڕێگا: فێڵکردن لە یوتوب لە ڕێگەی ناردنی داواکاری وەک ئەپی iOS
    """
    url = "https://www.youtube.com/youtubei/v1/player"
    
    # payloadی ئامادەکراوی iOS کە یوتوب هیچ کات بلۆکی ناكات
    payload = {
        "videoId": video_id,
        "context": {
            "client": {
                "clientName": "IOS",
                "clientVersion": "19.29.1",
                "deviceModel": "iPhone14,3",
                "osName": "iOS",
                "osVersion": "17.5.1.21F90",
                "hl": "en",
                "gl": "US"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "com.google.ios.youtube/19.29.1 (iPhone14,3; U; CPU iOS 17_5_1 like Mac OS X; en_US)"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # وەرگرتنی لینکی m3u8 لە بەشی streamingData
            streaming_data = data.get("streamingData", {})
            hls_manifest_url = streaming_data.get("hlsManifestUrl")
            
            if hls_manifest_url:
                return hls_manifest_url
    except Exception as e:
        print(f"Error fetching stream: {e}")
        
    return None

@app.route('/live/<video_id>')
def play_live(video_id):
    # کاتێک لینکەکە دەکرێتەوە ڕاستەوخۆ دەچێتە سەر لینکی m3u8ی نوێ
    m3u8_url = extract_m3u8_ios_client(video_id)
    if m3u8_url:
        return redirect(m3u8_url, code=302)
    return f"Error: Could not extract stream for '{video_id}'", 404

@app.route('/playlist.m3u')
def generate_playlist():
    host = Flask.request.host_url
    # کەناڵی لایڤی ۲٤/٧ی خۆت
    channels = [
        {"name": "24/7 Live Stream", "id": "hhkVU_7qZzM"}
    ]
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}", {ch["name"]}\n'
        m3u_content += f'{host}live/{ch["id"]}\n'
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
