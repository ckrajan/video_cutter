import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from werkzeug.utils import secure_filename
from moviepy.editor import *
import csv

# if not os.path.exists('static/uploads'):
# 	os.mkdir('static/uploads/')

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__, static_url_path='/static')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/")
def cutter():
    return render_template('cutter.html')

@app.route('/', methods=['POST'])
def upload_video():
	collection = request.form.get('collection')
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		flash('Video successfully uploaded and displayed below')
		return render_template('cutter.html', filename=filename, collection=collection)

@app.route('/upload_csv', methods=['POST'])
def upload():
	json_body = request.get_json()
	csv_str = json_body['csv']
	filename = json_body['filename']
	filename_only = os.path.splitext(filename)[0]

	reader = csv.reader(csv_str.splitlines(), skipinitialspace=True)
	chop_path = 'static/uploads/%s' % filename_only + '/'
	with open(chop_path + filename_only + '.csv', 'w') as out_file:
		writer = csv.writer(out_file)
		writer.writerows(reader)

@app.route('/chop_video', methods=['POST'])
def chop_video():
	json_body = request.get_json()
	rows_final = json_body['rows_final']
	filename = json_body['filename']
	filename_only = os.path.splitext(filename)[0]
	chop_path = 'static/uploads/%s' % filename_only + '/'

	if not os.path.exists('static/uploads/%s' % filename_only):
		os.mkdir(chop_path)

	for i in rows_final:
		clip = VideoFileClip(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		start_time = i[3]
		end_time = i[4]
		if(start_time != end_time):
			clip_x = clip.subclip(start_time, end_time)
			clip_x.write_videofile(os.path.join(chop_path, i[2] + ".mp4"))
	
	return filename

@app.route('/display/<filename>')
def display_video(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/uploaded_files', methods=['GET', 'POST'])
def uploaded_files():
	video_list = 'static/uploads/'
	allfiles = os.listdir(video_list)
	files = [ fname for fname in allfiles if fname.endswith('.mp4')]
	return files


if __name__ == '__main__':
    app.run(port=8080, debug=True)