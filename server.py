from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid

app = Flask(__name__, template_folder='templates')
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')

    if not url:
        return jsonify({'error': 'URL tidak ditemukan'}), 400

    unique_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.%(ext)s')

    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio',
        'quiet': True,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(unique_id):
                file_path = os.path.join(DOWNLOAD_FOLDER, file)
                return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Gagal mengunduh file'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
