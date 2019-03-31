#!/usr/bin/python3


import serial, sys, enum
import poller
import crc


class Framing(poller.Layer):
    def __init__(self, dev, bytes_min, bytes_max, timeout):

        self._bytes_min = bytes_min
        self._bytes_max = bytes_max
        self._state = "ocioso"
        self._dev = dev
        self._framesize = 0
        self._received = bytearray()
        self._frame = ""
        self.fd = dev
        self.timeout = timeout
        self.base_timeout = timeout
        self.disable_timeout()
        self._crc = crc.CRC16(" ")
        self._top = None

    def setTop(self, top):
        self._top = top

    def handle(self):
        byte = self._dev.read()
        
        self.handle_fsm(byte)
        
    def handle_timeout(self):
        print('Timeout !')
        self.handle_fsm(None)
        
    def send(self, frame):   
        self._crc.clear()
        self._crc.update(frame)
        msg = self._crc.gen_crc()
        self._dev.write(b'~')
        print (bytes([msg[len(frame)]]))
        a = msg[:len(frame)].decode('ascii')
        print (a)
        for i in range (len(msg)):
            #print (char)
           
            if (bytes([msg[i]]) == b'~' or bytes([msg[i]]) == b'}'):
                self._dev.write(b'}')
                if (bytes([msg[i]]) == b'~'):
                    self._dev.write(b'^')
                elif (bytes([msg[i]]) == b'}'):
                    self._dev.write(b']')
            else:              
                self._dev.write(bytes([msg[i]]))
        
        self._dev.write(b'~')
       

    def  handle_fsm(self, byte):

        if byte == None:
            self._state = "ocioso"
            self._ocioso(None)            
        elif self._state == "ocioso":
            self._ocioso(byte)
        elif self._state == "rx":
            self._rx(byte)
        elif self._state == "esc":
            self._esc(byte)            
            

    def _ocioso(self, byte):
        
        if byte is None:
            self._received.clear()
            self._frame = ""
            self._framesize = 0
            self.disable_timeout()
            
        elif((byte == b'~') and (self._framesize == 0)):
            self._state = "rx"       
            self.enable_timeout()
        else:
             self._state = "ocioso"
             self.disable_timeout()

    def frame(self, frame):
      
        self._frame = frame.decode('ascii')
        return self._frame
        
    def notifyLayer(self, dados):
        self._top.receiveFromBottom(dados)
    def _rx(self, byte):     
        
        if (self._framesize > self._bytes_max):
            self.disable_timeout()
            self._state = "ocioso"
            self._framesize = 0
            self._received.clear()
        elif(byte == b'~' and self._framesize >= self._bytes_min):
            print (self._received)
            self._crc.clear()
            self._crc.update(self._received)
            if self._crc.check_crc():
                self.notifyLayer(self._received[:self._framesize-2])              
            else:
                print ("nemrolou")
            self.disable_timeout()
            self._state = "ocioso"

            
            self._framesize = 0            
            self._received.clear()  
            

        elif(byte == b'}'):
            self._state = "esc"
        elif(byte == b'~' and self._framesize == 0):
            self._state = "rx"
        elif (byte != b'~' or byte != b'}'):
            
            self._received.append(int.from_bytes(byte, 'big'))
            self._framesize = self._framesize+1


    def _esc(self, byte):

       if(byte == b'~' or byte == b'}'):
           self._received.clear()
           self._framesize = 0
           self._state = "ocioso"
           self.disable_timeout()
       elif(byte == b'^'):
           self._received.append(int.from_bytes(b'~', 'big'))
           self._framesize = self._framesize + 1
           self._state = "rx"
       elif(byte == b']'):
           self._received.append(int.from_bytes(b'}', 'big'))
           self._framesize = self._framesize + 1
           self._state = "rx"
       


    def getDev(self):
        return self._dev

    def getRecebido(self):
        return self._received

    def getState(self):
        return self._state

