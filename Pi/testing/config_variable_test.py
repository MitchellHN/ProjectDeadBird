#/usr/bin/env python
# -*- coding: utf-8 -*-

import test_config
import threading

class Test_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print(test_config.altitude_pin)
        print(test_config._altitude_pin)

def test():
        print(test_config.altitude_pin)
        print(test_config._altitude_pin)

def main():
    test()
    test_thread = Test_Thread()
    test_thread.start()

if __name__ == '__main__':
    main()