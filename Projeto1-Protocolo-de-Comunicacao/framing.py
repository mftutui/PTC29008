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
        self._top = 1
        self._bottom = 1
        self._crc = crc.CRC16(" ")

    def handle(self):
        byte = self._dev.read()
        
        self.handle_fsm(byte)
        
    def handle_timeout(self):
        print('Timeout !')
        self.handle_fsm(None)
        
    def send(self, frame, framesize):   
        self._crc.clear()
        self._crc.update(frame)
        msg = self._crc.gen_crc()
        self._dev.write(b'~')
        print (msg)
        a = msg[:len(frame)].decode('ascii')
        print (a)
        for char in a:
            #print (char)
           
            if ((char) == '~' or (char) == '~'):
                self._dev.write(b'}')
                if ((char) == '~'):
                    self._dev.write(b'^')
                elif ((char) == '~'):
                    self._dev.write(b']')
            else:
              
                self._dev.write(bytes(char, 'ascii'))
       
        if (((bytes([msg[len(msg)-2]])) == b'~') or ((bytes([msg[len(msg)-2]])) == b'}')) :
             self._dev.write(b'}')
             if (bytes([msg[len(msg)-2]])) == b'~':
                self._dev.write(b'^')
             elif (bytes([msg[len(msg)-2]])) == b'}':
                self._dev.write(b']')
        else:
            self._dev.write(bytes([msg[len(msg)-2]]))
        
       
        if (((bytes([msg[len(msg)-1]])) == b'~') or ((bytes([msg[len(msg)-1]])) == b'}')) :
            self._dev.write(b'}')
            if (bytes([msg[len(msg)-1]])) == b'~':
                    self._dev.write(b'^')
            elif (bytes([msg[len(msg)-1]])) == b'}':
                self._dev.write(b']')
        else:
            self._dev.write(bytes([msg[len(msg)-1]]))



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
            
    
#    def receive(self):
#        while self._completeframe == 0:
#            self.handle_fsm()
#        received = self._received
#        self._completeframe = 0
#        return received

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
                print(self.frame(self._received[:self._framesize-2]))               
            else:
                print ("nemrolou")
            self.disable_timeout()
            self._state = "ocioso"

            
            self._framesize = 0            
           
            #self._top._notifyLayer(self.frame(self._received))
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

