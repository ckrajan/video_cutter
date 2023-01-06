import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from werkzeug.utils import secure_filename
from moviepy.editor import *
import csv

import cv2
import mediapipe as mp
import numpy as np
import math
import imutils
import jsonpickle

detector = mp.solutions.face_mesh.FaceMesh(
max_num_faces=10,
refine_landmarks=True,
min_detection_confidence=0.5,
min_tracking_confidence=0.5
)

mp_face_detection = mp.solutions.face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=0.5)

# frame_no = 10
arr_mouth = []
frame_counter = 1

outer_pts = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
inner_pts = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

left_eye_points = [159, 145]
right_eye_points = [386, 374]
nose_tip = [1]

if not os.path.exists('static/uploads'):
	os.makedirs('static/uploads/', exist_ok=True)

UPLOAD_FOLDER = 'static/uploads/'

outer_mouth = []
inner_mouth = []

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
	return filename

@app.route('/chop_video', methods=['POST'])
def chop_video():
	outer_mouth = []
	inner_mouth = []
	
	json_body = request.get_json()
	rows_final = json_body['rows_final']
	filename = json_body['filename']
	filename_only = os.path.splitext(filename)[0]
	chop_path = 'static/uploads/%s' % filename_only + '/'

	header = ['Filename', 'Clip_name', 'Frame', 'Outer_pts', 'Inner_pts']
	# data = []

	if not os.path.exists('static/uploads/%s' % filename_only):
		os.mkdir(chop_path)


	with open(chop_path + '/metadata.csv', 'w', encoding='UTF8', newline="") as f:
		writer = csv.writer(f)

		# write the header
		writer.writerow(header)

	for i in rows_final:
		clip = VideoFileClip(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		start_time = i[3]
		end_time = i[4]
		if(start_time != end_time):
			clip_x = clip.subclip(start_time, end_time)
			clip_x.write_videofile(os.path.join(chop_path, i[2] + ".mp4"))

			cap = cv2.VideoCapture(os.path.join(chop_path, i[2] + ".mp4"))

			fourcc = cv2.VideoWriter_fourcc(*'MP4V')
			# cap.get(3) is the video width, cap.get(4) is the video height.
			cap_width = int(cap.get(3))
			cap_height = int(cap.get(4))

			fps = cap.get(cv2.CAP_PROP_FPS)

			approx_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
			approx_frame_count_x = approx_frame_count - 1
			print("Total frames: {}".format(approx_frame_count))
			print("FPS :",fps)
			running = True
			frame_counter = 1

			out = cv2.VideoWriter(os.path.join(chop_path, i[2] + "_landmarks.mp4"), fourcc, fps, (cap_width, cap_height))

			while running:
				ret, frame = cap.read()
				if frame is not None:

					face_cnt = 0
					results = mp_face_detection.process(frame)

					if not results.detections:
						print('No faces detected',frame_counter)

						frame_result = process_frame(frame)
						keypoints = frame_result.multi_face_landmarks

						if(keypoints is not None):
							ls_single_face=keypoints[0].landmark 

							height, width, _ = frame.shape

							outer_mouth = drawlips("outer",frame,outer_pts,ls_single_face,height, width)
							inner_mouth = drawlips("inner",frame,inner_pts,ls_single_face,height, width)

							# frame = affine_transform_full(frame,ls_single_face,height, width)
							
					else:
						height, width, _ = frame.shape
						for detection in results.detections: # iterate over each detection and draw on image
							# mp_drawing.draw_detection(image, detection)
							bbox = detection.location_data.relative_bounding_box
							bbox_points = {
								"xmin" : int(bbox.xmin * width),
								"ymin" : int(bbox.ymin * height),
								"xmax" : int(bbox.width * width + bbox.xmin * width),
								"ymax" : int(bbox.height * height + bbox.ymin * height)
							}
							cropped_image = frame[bbox_points["ymin"]:bbox_points["ymax"], bbox_points["xmin"]:bbox_points["xmax"]]

							face_cnt = face_cnt + 1

							height_crop, width_crop, _ = cropped_image.shape
							
							frame_result1 = process_frame(cropped_image)
							keypoints1 = frame_result1.multi_face_landmarks
							if(keypoints1 is not None):
								ls_single_face1=keypoints1[0].landmark  

								outer_mouth = drawlips("outer",cropped_image,outer_pts,ls_single_face1,height_crop, width_crop)
								inner_mouth = drawlips("inner",cropped_image,inner_pts,ls_single_face1,height_crop, width_crop)
								
								# cropped_image = affine_transform_crop(cropped_image,ls_single_face1,height_crop, width_crop)

								frame[bbox_points["ymin"]:bbox_points["ymax"], bbox_points["xmin"]:bbox_points["xmax"]] = cropped_image
					
					csv_row = [filename_only, i[2], frame_counter, str(outer_mouth), str(inner_mouth)]

					# data.append(csv_row)

					with open(chop_path + '/metadata.csv', 'a', encoding='UTF8', newline="") as f:
						writer_1 = csv.writer(f)
						# write the data
						writer_1.writerow(csv_row)
						# writer.writerow("\n")

					out.write(frame)
					
					arr_mouth.clear()
					outer_mouth.clear()
					inner_mouth.clear()

				frame_counter = frame_counter + 1   
				if(frame_counter > approx_frame_count):
				# if(frame_counter > frame_no):  
					running = False
					out.release()




	return filename

def process_frame(frame):
    try:
        results = detector.process(frame)
        return results
        
    except Exception as e:
        print(e)


def drawlips(mouth,frame,pts,ls_single_face,height, width):
	for i in pts:
		pt1 = ls_single_face[i]
		x = int(pt1.x * width)
		y = int(pt1.y * height)

		coordinates = [x, y]
		arr_mouth.append(coordinates)
		
		# cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)

		if(mouth == "outer"):
			outer_mouth.append(coordinates)
		else:
			inner_mouth.append(coordinates)

	# new points for polygon
	# create and reshape array
	arr_mouth1 = np.array(arr_mouth)
	arr_mouth1 = arr_mouth1.reshape((-1, 1, 2))

	# Attributes
	isClosed = True
	color = (255, 0, 0)
	thickness = 2

	# draw closed polyline
	# cv2.polylines(frame, [arr_mouth1], isClosed, color, thickness)

	if(mouth == "outer"):
		return outer_mouth
		
	else:
		return inner_mouth

def affine_transform_full(frame,ls_single_face,height, width):
	angle_deg = eyes_angle(frame,left_eye_points,right_eye_points,nose_tip,ls_single_face,height, width)
	rotate_img = imutils.rotate(frame, angle=angle_deg)
	frame = rotate_img
	return frame

def affine_transform_crop(cropped_image,ls_single_face1,height_crop, width_crop):
	angle_deg = eyes_angle(cropped_image,left_eye_points,right_eye_points,nose_tip,ls_single_face1,height_crop, width_crop)
	rotate_img = imutils.rotate(cropped_image, angle=angle_deg)
	cropped_image = rotate_img
	return cropped_image

left_pts = []
right_pts = []

def eyes_angle(frame,left_eye_points,right_eye_points,nose_tip,ls_single_face,height, width):
    for i in left_eye_points:
        pt1 = ls_single_face[i]
        x1 = int(pt1.x * width)
        y1 = int(pt1.y * height)

        pts1  = [x1, y1]

        left_pts.append(pts1)
            
    for j in right_eye_points:
        pt2 = ls_single_face[j]
        x2 = int(pt2.x * width)
        y2 = int(pt2.y * height)

        pts2  = [x2, y2]
        right_pts.append(pts2)
    
    for k in nose_tip:
        pt3 = ls_single_face[k]
        x3 = int(pt3.x * width)
        y3 = int(pt3.y * height)

        cv2.circle(frame, (x3, y3), 1, (255, 0, 0), -1)
    
    mid_x1, mid_y1 =  (left_pts[0][0]+left_pts[1][0])/2, (left_pts[0][1]+left_pts[1][1])/2

    cv2.circle(frame, (int(mid_x1), int(mid_y1)), 1, (255, 0, 0), -1)

    mid_x2, mid_y2 =  (right_pts[0][0]+right_pts[1][0])/2, (right_pts[0][1]+right_pts[1][1])/2

    cv2.circle(frame, (int(mid_x2), int(mid_y2)), 1, (255, 0, 0), -1)
    
    # Angle between two eye mid-points
    myradians = math.atan2(int(mid_y1)-int(mid_y2), int(mid_x1)-int(mid_x2))
    mydegrees = math.degrees(myradians)

    if(mydegrees < 180 and mid_y1<mid_y2):
        res_angle = 180 - abs(mydegrees)
    else:
        res_angle = 180 + abs(mydegrees)
    return res_angle

@app.route('/display/<filename>')
def display_video(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/uploaded_files', methods=['GET', 'POST'])
def uploaded_files():
	video_list = 'static/uploads/'
	allfiles = os.listdir(video_list)
	files = [ fname for fname in allfiles if fname.endswith('.mp4')]
	return jsonpickle.encode(files)


if __name__ == '__main__':
    app.run(port=8080, debug=True)