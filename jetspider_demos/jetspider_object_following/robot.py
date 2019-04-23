import time
import traitlets
from traitlets.config.configurable import SingletonConfigurable
import serial

class Robot(SingletonConfigurable):
    def __init__(self, *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self.ser = serial.Serial('/dev/ttyACM1')
        
    def forward(self, speed=1.0, duration=None):
        self.ser.write(b'1')

    def backward(self, speed=1.0):
        self.ser.write(b'2')

    def left(self, speed=1.0):
        self.ser.write(b'3')

    def right(self, speed=1.0):
        self.ser.write(b'4')

    def stop(self):
        self.ser.write(b'5')
