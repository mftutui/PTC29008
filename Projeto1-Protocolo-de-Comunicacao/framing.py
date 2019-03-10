#!/usr/bin/python3

import serial, sys, enum
     

class Framing():
    def __init__(self, dev, bytes_min, bytes_max):
        
        self._bytes_min = bytes_min
        self._bytes_max = bytes_max
        self._state = "ocioso"
        self._dev = dev
        self._framesize = 0
        self._received = []
        self._completeframe = []

    def send(self, frame, framesize):
        self._dev.write(b'~')
        
        for char in frame:
            print(char)
            if (char == '~' or char == '}'):
                self._dev.write(b'}')
                if (char == '~'):
                    self._dev.write(b'^')
                elif (char == '}'):
                    self._dev.write(b']')
            else:
                self._dev.write(bytes(char, 'utf-8'))
                
        self._dev.write(b'~')

    def  handle(self):
        print('>>>', self.getState())
        self.setState()

    def _ocioso(self):
        byte = self._dev.read()
        
        if((byte == b'~') and (self._framesize == 0)):
            self._state = "rx"
        else:
            self._state = "ocioso"

    def _rx(self):
        byte = self._dev.read()
        print ("Byte recebido: " + str(byte))
        if (self._framesize > self._bytes_max):
            self._state = "ocioso"
            self._framesize = 0
            self._received.clear()          
        elif(byte == b'~' and self._framesize >= self._bytes_min):
            self._state = "ocioso"
            self._framesize = 0
            self._received.clear()          
        elif(byte == b'}'):
            self._state = "esc"
        elif(byte == b'~' and self._framesize == 0):
            self._state = "rx"
        elif (byte != b'~' or byte != b'}'):
            self._received.append(byte)
            self._framesize = self._framesize+1
        

    def _esc(self):
       byte = self._dev.read()
       print ("Byte recebido: " + str(byte))
       if(byte == b'~' or byte == b'}'):
           self._received.clear()
           self._framesize = 0
           self._state = "ocioso"
       elif(byte == b'^'):
           self._received.append(b'~')
           self._framesize = self._framesize + 1
           self._state = "rx"
       elif(byte == b']'):
           self._received.append(b'}')
           self._framesize = self._framesize + 1
           self._state = "rx"
       else:
            self._state = "rx"
    
    def getRecebido(self):
        return self._received

    def setState(self):
        if self._state == "ocioso":
            self._ocioso()
        elif self._state == "rx":
            self._rx()
        elif self._state == "esc":
            self._esc()

    def getState(self):
        return self._state

