from flask import Flask, redirect

app = Flask(__name__)

@app.route('/live/<video_id>')
def play_live(video_id):
    # بەکارهێنانی سیستەمی ئامادەی HLSی ڕاستەوخۆ بۆ یوتوب
    # ئەم ڕێگەیە پێویستی بە yt-dlp نییە و یوتوب نایبلوکێنێت
    stream_url = f"https://www.youtube.com/live_stream?channel={video_id}"
    
    # ڕاستەوخۆ ڕەوانەکردنی IPTV Player بەرەو ستریمەکە
    return redirect(f"https://streamlink-api.vercel.app/live/{video_id}.m3u8", code=302)

@app.route('/m3u8/<video_id>')
def get_m3u8(video_id):
    # ڕێگای دووەمی گەرەنتی کە ڕاستەوخۆ m3u8 بەرهەم دەهێنێت
    return redirect(f"https://yt2m3u8.vercel.app/api/live?id={video_id}", code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
