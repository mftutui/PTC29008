#!/usr/bin/python3

import serial, sys, enum

class Framming():
    def __init__(self):
        #self.dev = dev
        #self.bytes_min = bytes_min
        #self.bytes_max = bytes_max
        self.estado = "ocioso"

    def  handle(self):
        print('>>>', self.getState())
        self.setState()

    def _ocioso(self):
        self.estado = "rx"

    def _rx(self):
        self.estado = "esc"

    def _esc(self):
        self.estado = "ocioso"

    def setState(self):
        if self.estado == "ocioso":
            self._rx()
        elif self.estado == "rx":
            self._esc()
        elif self.estado == "esc":
            self._ocioso()

    def getState(self):
        return self.estado 

if __name__ == '__main__':
    enq = Framming()
    for x in range(10):
        enq.handle()