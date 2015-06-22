#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPIO
import camera_controller

class Motion_Controller():
    
    #Creation method.
    #   camera_controller:
    #       Camera control module used for move_to_pixel(). Camera_Controller.
    def __init__(self, camera_controller, config):
        RPIO.set_mode(RPIO.BCM)
        self.config = config
        self.servo_channels = []
        self.channel_cycles = []
        self.servos = {}
        self.actuators = {}
        self.camera_controller = camera_controller
        self.used_pins = []
            
    #Add a servo to controller.
    #   name:
    #       Name of the servo. Arbitrary type, but typically a string.
    #   pin:
    #       GPIO pin connected to servo. Integer.
    #   range_of_motion (default 90):
    #       Servo's range of motion in degrees. Numeric.
    #   pulse (default [1.0, 2.0]):
    #       Maximum and minimum pulse length in mS. List of form [min, max].
    #   reverse (default False):
    #       Whether to reverse move commands before executing. Boolean.
    #   update (default:
    #       The update cycle length in uS. Integer.
    def add_servo(self, name, pin, range_of_motion = 90, pulse = [1.0, 2.0], 
                  reverse = False, update = 20000):
        assert pin not in self.used_pins
        #Create RPIO servo object if none exist with the correct update cycle,
        #otherwise use existing object with correct update cycle
        if update in self.channel_cycles:
            servo = self.channel_cycles.index(update)
        else:
            assert len(self.channel_cycles) <= 15
            servo = len(self.channel_cycles)
            self.servo_channels.append(RPIO.PWM.servo(servo, update))
            self.channel_cycles.append(update)
        self.servos[name] = {'servo': servo, 
                             'pin': pin, 
                             'update': update, 
                             'pulse': [float(pulse[0]), float(pulse[1])], 
                             'range': range_of_motion, 
                             'reverse': reverse,
                             'position': range_of_motion / 2.0
                             }
        self.used_pins.append(pin)
    
    #Add a linear actuator to controller                         
    def add_actuator(self, name, pin, kind = 'pull'):
        assert pin not in self.used_pins
        assert kind in ['push',
                        'pull']
        if kind == 'push':
            position = 'in'
        elif kind == 'pull':
            position = 'out'
        RPIO.setup(pin, RPIO.out)
        self.actuators[name] = {'pin': pin,
                                'kind': kind,
                                'position': position
                                }
        
    #Sets all servos and actuators
    def update(self):
        for servo in self.servos:
            #Correct position if out of bound
            self.servos[servo]['position'] %= 360
            if self.servos[servo]['position'] > self.servos[servo]['range']:
                self.servos[servo]['position'] = self.servos[servo]['range']
            #Calculate pulse
            pulse_min = min(self.servos[servo]['pulse'])
            pulse_max = max(self.servos[servo]['pulse'])
            position = self.servos[servo]['position']
            range_of_motion = self.servos[servo]['range']
            position_ratio = position / range_of_motion
            pulse =  position_ratio * (pulse_max - pulse_min) + pulse_min
            #Set servo
            pin = self.servos[servo]['pin']
            self.servo_channels[self.servos[servo]['servo']].set_servo(pin, pulse)
        for actuator in self.actuators:
            position = 1 if self.actuators[actuator]['position'] == 'in' else 0
            pin = self.actuators[actuator]['pin']
            if self.actuators[actuator]['kind'] == 'push':
                RPIO.output(pin, abs(position - 1))
            else:
                RPIO.output(pin, position)
            
    #Move a servo
    #   servo_name:
    #       The name assigned to the servo at creation.
    #   change:
    #       The degree change.
    def move(self, servo_name, change):
        #Invert change if the servo has been set to be reversed.
        change *= -1 if self.servos[servo_name]['reverse'] else 1
        self.servos[servo_name]['position'] += change
        self.update()
    
    #Move an arbitrary number of servos to a particular conficuration. 
    #   servo_angles:
    #       The servos to move and the angles to move to. Dictionary of the 
    #       form {servo_name: angle}, where servo_name is the name assigned to 
    #       the servo and angle is the angle in degrees. Only servos to be 
    #       changed need be listed.
    def move_to_angle(self, servo_angles):
        for servo_name in servo_angles:
            position = self.servos[servo_name]['position']
            change = servo_angles[servo_name] - position
            self.move(servo_name, change)
    
    #Move to a pixel on the camera.
    #   pixel_target:
    #       The pixel to move to. List of the form [x, y] with 0,0 in top right.
    #   altitude_Servo:
    #       The name assigned to the servo controlling altitude (y on camera).
    #   azimuth_servo:
    #       The name assigned to the servo controllng azimuth (x on camera).
    def move_to_pixel(self, pixel_target, altitude_servo = 'altitude',
                      azimuth_servo = 'azimuth'):
        resolution = self.camera_controller.resolution
        field_of_view = self.camera_controller.field_of_view
        crosshair_calibration = self.camera_controller.crosshair_calibration
        #Calculate altitude and azimuth change
        degrees_per_pixel = [degree / pixel for pixel, degree in 
                             zip(resolution, field_of_view)]
        pixel_change = [calibration - pixel for calibration, pixel in
                        zip(crosshair_calibration, pixel_target)]
        degree_change = [convert * pixel for convert, pixel in 
                         zip(degrees_per_pixel, pixel_change)]
        self.move(azimuth_servo, degree_change[0])
        self.move(altitude_servo, degree_change[1])
