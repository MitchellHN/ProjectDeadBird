#/usr/bin/env python
# -*- coding: utf-8 -*-

import UI.CommandLine.gui as gui
import threading
import queue
import random
import time
import tkinter

def command(queue, stop):
    commands = ['error',
                'move',
                'set safety',
                'fire',
                'move reticle',
                'store location',
                'get reticle',
                'get altitude',
                'get azimuth',
                'get safety',
                'get locations',
                '0x0',
                '0x10',
                '0x11',
                '0x12',
                '0x13',
                '0x14']
    count = 0
    while True:
        if stop.is_set():
            break
        if count % 10 == 11:
            command = random.choice(commands)
            queue.put([command, 0])
        count += 1
        time.sleep(1)


read_queue = queue.Queue()
write_queue = queue.Queue()
stop = threading.Event()
root = tkinter.Tk()
io = gui.Input(root, read_queue, write_queue, stop)
command_thread = threading.Thread(target=command, args=(read_queue, stop))
command_thread.start()
io.mainloop()
stop.set()