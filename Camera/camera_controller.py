#!/usr/bin/env python
# -*- coding: utf-8 -*-

import picamera
import socket
import picamera.array
import cv2

class Camera_Controller():
    
    def __init__(self, stream):
        self.camera = picamera.Picamera()
        self.camera.resolution = [640, 480]
        self.camera.framerate = 24
        self.field_of_view = [53.5, 41.41]
        self.connection = stream.accept()[0].makefile('wb')
        self.crosshair_calibration = [320, 230]
        
    def begin_transmission(self):
        self.camera.start_recording(self.connection, format='h264')
        
    def end_transmission(self):
        self.camera.stop_recording()
        
    def get_opencv(self):
        with picamera.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format='bgr', use_video_port=True)
            # At this point the image is available as stream.array
            image = stream.array
        return image
    
#Used in with...as statements to create and automatically destroy the
#camera controller
class Camera_Constructor():
    
    def __init__(self, stream):
        self.controller = Camera_Controller(stream)
    
    def __enter__(self):
        return self.controller
    
    def __exit__(self, type, value, traceback):
        self.controller.camera.close()
        self.controller.connection.close()