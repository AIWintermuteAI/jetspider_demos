#!/usr/bin/env python3

#
# Teleopration for jetspider
from importlib import import_module
import time
import serial
from flask import Flask, render_template, request, Response
from camera_opencv import Camera

app = Flask (__name__, static_url_path = '')

try:
   # Change the baud rate here if diffrent than 19200
   uno = serial.Serial('/dev/ttyACM0', 9600)
except IOError:
   print("Comm port not found")
   sys.exit(0)


# A little dwell for settling down time
time.sleep (3)

#
# URI handlers - all the bot page actions are done here
#

# Send out the bots control page (home page)
@app.route ("/")
def index ( ):
   return render_template ('index.html', name = None)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route ("/forward")
def forward ( ):

   print("Forward")
   go_forward()

   # sleep 100ms + run_time
   time.sleep (0.100 + run_time)

   return "ok"

@app.route ("/backward")
def backward ( ):
   global last_direction, run_time

   print("Backward")
   go_backward()

   # sleep 100ms + run_time
   time.sleep (0.100 + run_time)

   return "ok"

@app.route ("/left")
def left ( ):

   print("Left")
   go_left()

   # sleep @1/2 second
   time.sleep (0.500 - turn_tm_offset)

   return "ok"

@app.route ("/right")
def right ( ):
   print("Right")
   go_right()

   # sleep @1/2 second
   time.sleep (0.500 - turn_tm_offset)

   return "ok"


@app.route ("/stop")
def stop ( ):
   halt()

   # sleep 100ms
   time.sleep (0.100)
   return "ok"

#
# Motor drive functions
#
def go_forward():
	uno.write(b'1')

def go_backward():
	uno.write(b'2')

def go_left():
    uno.write(b'4')

def go_right():
    uno.write(b'3')
def halt():
    uno.write(b'5')

if __name__ == "__main__" :
   app.run (host = '0.0.0.0', port = 80, debug = True)
