#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl
import config
try:
    import picamera
except (ImportError, SystemError):
    print("Couldn't import picamera")
try:
    import cv2
except ImportError:
    print("Couldn't import cv2")

#============================================================================
# Config
# ----
#   This file contains a class (Camera_Controller) for high-level control
#   of the Raspberry Pi camera module and piping its output to a socket.
#   It also contains a dummy class (Dummy_Camera_Controller) for simulating
#   control when the camera module isn't connected, the UI does not use
#   video, or for testing on a different system, a dummy class (Dummy_Camera)
#   that simulates picamera.PiCamera for the dummy controller class, and
#   a context manager class (Camera_Constructor) for the two controllers.

#USed to control a Raspberry Pi camera module.
class Camera_Controller():
    
    #Creation method
    #   stream:
    #       The socket to which the camera should transmit. Socket.
    def __init__(self, server_socket):
        self.camera = picamera.PiCamera()
        self.camera.resolution = [640, 480]
        self.camera.framerate = 24
        self.field_of_view = config.__fov
        self.connection = server_socket.makefile('wb')
        self.crosshair_calibration = config.__calibration
        
    def begin_transmission(self):
        if config.echo:
            print('Beginning camera transmission')
        self.camera.start_recording(self.connection, format='h264')
        
    def end_transmission(self):
        if config.echo:
            print('Ending camera transmission')
        self.camera.stop_recording()
        
    def get_opencv(self):
        with picamera.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format='bgr', use_video_port=True)
            # At this point the image is available as stream.array
            image = stream.array
        return image
    

#Used to simulate control over camera
class Dummy_Camera_Controller():
    #Creation method
    def __init__(self):
        self.camera = Dummy_Camera()
        self.camera.resolution = [640, 480]
        self.camera.framerate = 24
        self.field_of_view = [53.5, 41.41]
        self.crosshair_calibration = [320, 230]
        
    def begin_transmission(self):
        if config.echo:
            print('Beginning camera transmission')
        
    def end_transmission(self):
        if config.echo:
            print('Ending camera transmission')
        
    def get_opencv(self):
        return None
            
#Used by Dummy_Camera_Controller as a substitute for picamera.PiCamera.
class Dummy_Camera():
    def __init__(self):
        resolution = None
        framerate = None
        
    def close(self):
        resolution = None


#Used in with...as statements to create and automatically destroy the
#camera controller and its dummy.
class Camera_Constructor():
    
    #Creation method
    #   stream:
    #       The socket to which the camera should transmit. SSLSocket for 
    #       camera controller or any other type for its dummyl
    def __init__(self, stream):
        if isinstance(stream, ssl.SSLSocket):
            self.controller = Camera_Controller(stream)
        else:
            self.controller = Dummy_Camera_Controller()
    
    def __enter__(self):
        return self.controller
    
    def __exit__(self, type, value, traceback):
        if isinstance(self.controller, Camera_Controller):
            self.controller.camera.close()
            self.controller.connection.close()