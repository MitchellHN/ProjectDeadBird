#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from . import config
import math
import threading


class Control_Process(threading.Thread):
    def __init__(self, camera_queue, motion_controller, read_queue, server_queue, stop):
        threading.Thread.__init__(self, name = 'control')
        self.camera_queue = camera_queue
        self.motion_controller = motion_controller
        self.read_queue = read_queue
        self.server_queue = server_queue
        self.stop = stop
        self.commands = {'error': self.error,
                         'move to pixel': self.move_to_pixel,
                         'move to altitude': self.move_to_altitude,
                         'change altitude': self.change_altitude,
                         'move to azimuth': self.move_to_azimuth,
                         'change azimuth': self.change_azimuth,
                         'move to location': self.move_to_location,
                         'set safety': self.set_safety,
                         'fire': self.fire,
                         'move reticle': self.move_reticle,
                         'store location': self.store_location,
                         'send reticle': self.send_reticle,
                         'send altitude': self.send_altitude,
                         'send azimuth': self.send_azimuth,
                         'send safety': self.send_safety,
                         'send locations': self.send_locations,
                         'reticle ==': self.reticle_equals}
        self.errors = {}

    def run(self):
        while True:
            if self.stop.is_set():
                break
            if not self.read_queue.empty():
                # Get command from queue
                q = self.read_queue.get()
                # Extract command and arguments (if any)
                if isinstance(q, list):
                    command = q.pop(0)
                    arguments = q
                elif isinstance(q, str):
                    command = q
                    arguments = []
                else:
                    raise TypeError('Something other than list or str was ' +
                                    'added to the control queue.')
                    # Try to execute command, raise errors if necessary
                try:
                    self.commands[command](*arguments)
                except KeyError:
                    print("%r is not an acceptable control command" % command)
                    raise
                except TypeError:
                    message = "The %r command was given the arguments %r" % (command, arguments)
                    print(message)
                    raise

    def pixel_to_coordinates(self, pixel):
        width = self.motion_controller.camera_controller.camera.resolution[0]
        height = self.motion_controller.camera_controller.camera.resolution[1]
        x = pixel % width
        y = math.trunc(pixel / width)
        assert x < width
        assert y < height
        return x, y

    def coordinates_to_pixel(self, x, y):
        width = self.motion_controller.camera_controller.camera.resolution[0]
        height = self.motion_controller.camera_controller.camera.resolution[1]
        assert x < width
        assert y < height
        return y * width + x

    def error(self, error_code):
        pass

    def move_to_pixel(self, pixel):
        x, y = self.pixel_to_coordinates(pixel)
        if config.echo:
            print('Moving to pixel %s by %s.' % (x, y))
        self.motion_controller.move_to_pixel([x, y])

    def move_to_altitude(self, altitude):
        if config.echo:
            print('Moving to altitude %s.' % altitude)
        self.motion_controller.move_to_angle({'altitude': altitude})

    def change_altitude(self, change):
        if config.echo:
            print('Changing altitude by %s.' % change)
        self.motion_controller.move('altitude', change)

    def move_to_azimuth(self, azimuth):
        if config.echo:
            print('Moving to azimuth %s.' % azimuth)
        self.motion_controller.move_to_angle({'azimuth': azimuth})

    def change_azimuth(self, change):
        if config.echo:
            print('Changing azimuth by %s.' % change)
        self.motion_controller.move('azimuth', change)

    def move_to_location(self, location):
        pass

    def set_safety(self, on_off):
        if on_off == 'on':
            position = config._safety_on_position
        elif config._safety_on_position == 'in':
            position = 'out'
        else:
            position = 'in'
        if config.echo:
            print('Safety actuator set to ' + position + '.')
        config.safety = on_off
        self.motion_controller.actuate('safety', position)

    def fire(self):
        if config.safety == 'off':
            if config.echo:
                print('Firing.')
            self.motion_controller.pulse_actuator('trigger',
                                                  config._fire_duration,
                                                  config._fire_position)
        else:
            if config.echo:
                print('Cannot fire; safety is on.')

    def move_reticle(self, pixel):
        x, y = self.pixel_to_coordinates(pixel)
        if config.echo:
            print('Moving reticle to %s by %s.' % (x, y))
        self.camera_queue.put(['move reticle', x, y])

    def store_location(self):
        pass

    def send_reticle(self):
        self.camera_queue.put(['get reticle'])

    def send_altitude(self):
        altitude = self.motion_controller.servos['altitude']['position']
        self.server_queue.put(['send altitude', altitude])

    def send_azimuth(self):
        azimuth = self.motion_controller.servos['azimuth']['position']
        self.server_queue.put(['send azimuth', azimuth])

    def send_safety(self):
        safety_position = self.motion_controller.actuators['safety']['position']
        if config._safety_on_position == 'in':
            safety = 'on' if safety_position == 'in' else 'off'
        else:
            safety = 'on' if safety_position == 'out' else 'off'
        self.server_queue.put(['send safety', safety])

    def send_locations(self):
        pass

    def reticle_equals(self, x, y):
        pixel = self.coordinates_to_pixel(x, y)
        self.server_queue.put(['send reticle', pixel])
