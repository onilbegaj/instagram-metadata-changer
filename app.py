import os
import ffmpeg
from flask import Flask, request, render_template, send_from_directory, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Route to render the upload page
@app.route('/')
def index():
    return render_template('index.html')

# Process the uploaded video with modifications
def process_video(input_video_path, num_videos):
    output_files = []
    for i in range(num_videos):
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"video_{i+1}.mp4")
        stream = ffmpeg.input(input_video_path)
        stream = stream.filter('eq', brightness=0.01 * (i % 2), contrast=1.0 + 0.01 * (i % 3))
        stream = stream.output(output_path)
        ffmpeg.run(stream)
        output_files.append(output_path)
    return output_files

# Endpoint to upload video
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'count' not in request.form:
        return redirect(request.url)
    file = request.files['file']
    num_videos = int(request.form.get('count'))
    if file.filename == '' or num_videos < 1:
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        processed_files = process_video(file_path, num_videos)
        return render_template('downloads.html', files=processed_files)

# Serve processed files for download
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
