#!/usr/bin/python3

import serial, sys, enum
import poller


class Framing(poller.Callback):
    def __init__(self, dev, bytes_min, bytes_max, timeout):

        self._bytes_min = bytes_min
        self._bytes_max = bytes_max
        self._state = "ocioso"
        self._dev = dev
        self._framesize = 0
        self._received = []
        self._completeframe = 0
        self.fd = dev
        self.timeout = timeout
        self.base_timeout = timeout
       

    def handle(self):
        byte = self._dev.read()
        self.handle_fsm(byte)
        
    def handle_timeout(self):
        print('Timeout !')
        self.handle_fsm(None)
        
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

        

    def  handle_fsm(self, byte):
        print ("Byte recebido: " + str(byte))
        print('>>>', self.getState())
        if byte == None:
            self._state = "ocioso"
            self._ocioso(None)            
        elif self._state == "ocioso":
            self._ocioso(byte)
        elif self._state == "rx":
            self._rx(byte)
        elif self._state == "esc":
            self._esc(byte)            
            
    
#    def receive(self):
#        while self._completeframe == 0:
#            self.handle_fsm()
#        received = self._received
#        self._completeframe = 0
#        return received

    def _ocioso(self, byte):
        if byte is None:
            self._received.clear()
            self._framesize = 0
        elif((byte == b'~') and (self._framesize == 0)):
            self._state = "rx"
        else:
             self._state = "ocioso"

    def _rx(self, byte):
        
        
        if (self._framesize > self._bytes_max):
            self._state = "ocioso"
            self._framesize = 0
            self._received.clear()
        elif(byte == b'~' and self._framesize >= self._bytes_min):
            self._state = "ocioso"
            self._framesize = 0
            print ("Quadro >>>", self._received)
            

        elif(byte == b'}'):
            self._state = "esc"
        elif(byte == b'~' and self._framesize == 0):
            self._state = "rx"
        elif (byte != b'~' or byte != b'}'):
            self._received.append(byte)
            self._framesize = self._framesize+1


    def _esc(self, byte):
       
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
       


    def getDev(self):
        return self._dev

    def getRecebido(self):
        return self._received

   
        

    def getState(self):
        return self._state
