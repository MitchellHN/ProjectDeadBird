#!/usr/bin/env python
# -*- coding: utf-8 -*-

import picamera
from PIL import Image

class Camera_Controller():
    
    def __init__(self, stream = "output"):
        self.camera = picamera.Picamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 24
        self.target_luminance = 128
    
    #Used with "with...as" statements to create the camera controller
    def __enter__(self):
        return self
    
    #Used with "with...as" statements to automatically clean up the camera controller
    def __exit__(self, type, value, traceback):
        self.camera.close()