#!/usr/bin/python3
import serial, sys, enum

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

    def _tx(self,lista):


        self.estado = "esc"

    def _esc(self):
        self.estado = "ocioso"

    def setState(self, lista):
        if self.estado == "ocioso":
            self._rx(lista)
        elif self.estado == "rx":
            self._esc()
        elif self.estado == "esc":
            self._ocioso()

    def getState(self):
        return self.estado

if __name__ == '__main__':
    enq = Framming()
    ser = serial.Serial('/dev/pts/12')

    seq = ['~', 'a', 'b', 'c', '~']
    if enq.estado == "ocioso" and seq[0] == '~' :
        enq.setState(seq)
