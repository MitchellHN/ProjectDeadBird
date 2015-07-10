#/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import tkinter
import socket
import ssl
import queue
import time
import UI.CommandLine.gui as gui

DATA_PORTS = [8090, 8091, 8092, 8093]
ADDRESS = ''

class Receive_Thread(threading.Thread):

    def __init__(self, sock, queue, stop_event):
        threading.Thread.__init__(self)
        self.sock = sock
        self.queue = queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                print(self.stop_event.is_set())
                data = self.sock.recv(4)
                if data:
                    command = hex(data[0])
                    argument = bytes([data[1], data[2], data[3]])
                    self.queue.put([command, argument])
            except socket.timeout:
                pass
            except:
                raise
        print('ending receive thread')

class Send_Thread(threading.Thread):

    def __init__(self, sock, queue, stop_event):
        threading.Thread.__init__(self)
        self.sock = sock
        self.queue = queue
        self.stop_event = stop_event
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
                         'get reticle': self.get_reticle,
                         'get altitude': self.get_altitude,
                         'get azimuth': self.get_azimuth,
                         'get safety': self.get_safety,
                         'get locations': self.get_locations}

    def run(self):
        while not self.stop_event.is_set():
            if not self.queue.empty():
                q = self.queue.get()
                if isinstance(q, list):
                    command = q.pop(0)
                    arguments = q
                else:
                    command = q
                    arguments = [0]
                # Try to execute command, raise errors if necessary
                try:
                    self.commands[command](*arguments)
                except KeyError:
                    print("%r is not an acceptable send command" % command)
                except TypeError:
                    message = ("The %r command was given the arguments %r" %
                               (command, arguments))
                    print(message)
                    raise
        print('ending send thread')

    def error(self, code):
        self.send(0, code)

    def move_to_pixel(self, pixel):
        self.send(16, pixel)

    def move_to_altitude(self, altitude):
        self.send(17, altitude)

    def change_altitude(self, change):
        self.send(18, change, True)

    def move_to_azimuth(self, azimuth):
        self.send(19, azimuth)

    def change_azimuth(self, change):
        self.send(20, change, True)

    def move_to_location(self, id):
        self.send(21, id)

    def set_safety(self, position):
        argument = 'ffffff' if position == 'on' else '000000'
        self.send(22, bytes.fromhex(argument))

    def fire(self, arg):
        self.send(23, 0)

    def move_reticle(self, pixel):
        self.send(48, pixel)

    def store_location(self, arg):
        self.send(49, 0)

    def get_reticle(self, arg):
        self.send(80, 0)

    def get_altitude(self, arg):
        self.send(81, 0)

    def get_azimuth(self, arg):
        self.send(82, 0)

    def get_safety(self, arg):
        self.send(83, 0)

    def get_locations(self, arg):
        self.send(84, 0)

    def send(self, command, argument, is_signed=False):
        assert type(argument) in [int, bytes]
        if isinstance(argument, int):
            argument = argument.to_bytes(3, 'big', signed=is_signed)
        message = command.to_bytes(1, 'big') + argument
        self.sock.send(message)

def connect():
    sock = ssl.wrap_socket(socket.socket(socket.AF_INET,
                                         socket.SOCK_STREAM),
                           server_side = False)
    port_number = 0
    while True:
        try:
            sock.connect((ADDRESS, DATA_PORTS[port_number]))
        except ConnectionRefusedError:
            if port_number < len(DATA_PORTS) - 1:
                port_number += 1
            else:
                print('ran out of ports')
                raise
        else:
            break
    time.sleep(1)
    sock.send((0).to_bytes(3, 'big'))
    return sock

def kill(threads, stop, fail):
    for thread in threads:
        thread.start()
    while not stop.is_set():
        alive = [i.is_alive() for i in threads]
        if not all(alive):
            fail.set()
            print('a thread died')
            break

    print('stop is set')


def main():
        sock = connect()
        fail = threading.Event()
    try:
        print('connected')
        sock.settimeout(0.250)
        send_queue = queue.Queue()
        receive_queue = queue.Queue()
        stop = threading.Event()
        receive_thread = Receive_Thread(sock, receive_queue, stop)
        send_thread = Send_Thread(sock, send_queue, stop)
        threads = [receive_thread, send_thread]
        root = tkinter.Tk()
        window = gui.Input(root, receive_queue, send_queue, stop)
        kill_thread = threading.Thread(target=kill, args=(threads, stop, fail))
        kill_thread.start()
        root.mainloop()
    finally:
        if fail.is_set():
            sock.send(b'\x00\x00\x00\x00')
        else:
            sock.send(b'\xE0\x00\x00\x00')
        sock.close()

if __name__ == '__main__':
    main()