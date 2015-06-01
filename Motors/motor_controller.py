#!/usr/bin/env python
# -*- coding: utf-8 -*-

from RPIO import PWM

#Default update cycle length (mS)
UPDATE = 20

#Default ulse length [min, max] (ms)
PULSE = [1.0, 2.0]

#Default servo range (degrees)
RANGE = 90

class Motor_Controller():
    
    def __init__(self, servos, pins, updates = '', pulses = '', ranges = ''):
        self.servos = {}
        for servo_name in servos:
            #Pin number
            pin = pins[servo_name]
            #update cycle length (ms)
            update = UPDATE if updates == '' else updates[servo_name]
            #Pulse length range [min, max] (ms)
            pulse = PULSE if pulses == '' else pulses[servo_name]
            #Range of motion (degrees)
            range_of_motion = RANGE if ranges == '' else ranges[servo_name]
            #Create servo
            servo = PWM.servo(0, update)
            self.servos[servo_name] = {'servo': servo, 'pin': pin, 'update': update, 'pulse': pulse, 'range': range_of_motion, 'position': range_of_motion / 2}
        
    def update(self):
        for servo in self.servos:
            pulse = (servo['position'] / servo['range']) * (max(servo['pulse']) -  min(servo['pulse'])) + min(servo['pulse'])
            servo['servo'].set_servo(servo['pin'], pulse)
            
        
    def move(self, servo_name, position):
        self.servos[servo_name]['position'] = position
        self.update()
    
    def move_to(self, servo_angles):
        for servo_name in servo_angles:
            self.move(self.servos[servo_name], servo_angles[servo_name])