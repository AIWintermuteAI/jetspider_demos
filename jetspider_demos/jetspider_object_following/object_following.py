#!/usr/bin/env python3

import cv2
from jetbot import ObjectDetector
import os
import numpy as np
import time
from flask import Flask, render_template, Response
from importlib import import_module
from categories import *
import robot

robot = Robot()

model = ObjectDetector('ssd_mobilenet_v2_coco.engine')

camera = cv2.VideoCapture(0)
app = Flask(__name__)

start = 0
isObject = False
isMoving = False
width = 300
height = 300

def detection_center(detection):
    """Computes the center x, y coordinates of the object"""
    bbox = detection['bbox']
    center_x = (bbox[0] + bbox[2]) / 2.0 - 0.5
    center_y = (bbox[1] + bbox[3]) / 2.0 - 0.5
    return (center_x, center_y)
    
def norm(vec):
    """Computes the length of the 2D vector"""
    return np.sqrt(vec[0]**2 + vec[1]**2)

def closest_detection(detections):
    """Finds the detection closest to the image center"""
    closest_detection = None
    for det in detections:
        center = detection_center(det)
        if closest_detection is None:
            closest_detection = det
        elif norm(detection_center(det)) < norm(detection_center(closest_detection)):
            closest_detection = det
    return closest_detection

def execute(img):
    global width
    global height
    global isObject
    global isMoving
    global start
    
    image = cv2.resize(img, (300,300))
        
    # compute all detected objects
    detections = model(image)
    
    # draw all detections on image
    for det in detections[0]:
        bbox = det['bbox']
        text = str(category_map[det['label']])
        cv2.rectangle(image, (int(width * bbox[0]), int(height * bbox[1])), (int(width * bbox[2]), int(height * bbox[3])), (255, 0, 0), 2)
        cv2.putText(image, text, (int(width * bbox[0]), int(height * bbox[3])), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), lineType=cv2.LINE_AA) 
    
    # select detections that match selected class label
    matching_detections = [d for d in detections[0] if d['label'] == 53]
    
    # get detection closest to center of field of view and draw it
    det = closest_detection(matching_detections)
    if det is not None:
        bbox = det['bbox']
        cv2.rectangle(image, (int(width * bbox[0]), int(height * bbox[1])), (int(width * bbox[2]), int(height * bbox[3])), (0, 255, 0), 5)

    if det is None:
        if isObject == True:
            start = time.time()
            isObject = False
        if (time.time() - start) > 4:
            robot.stop()
        
    # otherwsie steer towards target
    else:
        if isMoving == False:
            start = time.time()
            isMoving = True
            center = detection_center(det)
            print(center)
            # move robot forward and steer proportional target's x-distance from center
            if center[0] > 0.2:
                print('left')
                robot.left()
            elif center[0] < -0.2:
                print('right')
                robot.right()
            elif center[0] > -0.2 and center[0] < 0.2:
                print('forward')
                robot.forward() 
        if (time.time() - start) > 2:
            isMoving = False

    return cv2.imencode('.jpg', image)[1].tobytes()


@app.route('/')
def index():
    return render_template('index.html')


def gen():
    while True:
        ret, frame = camera.read()
        image = execute(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host='0.0.0.0', port = 80, threaded=True)