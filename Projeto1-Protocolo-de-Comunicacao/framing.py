#!/usr/bin/python3


import poller
import crc



class Framing(poller.Layer):
    idle = 1
    rx = 2
    esc = 3

    def __init__(self, dev, bytes_min, bytes_max, timeout):
        self._bytes_min = bytes_min
        self._bytes_max = bytes_max
        self._state = self.idle
        self._dev = dev
        self._framesize = 0
        self._received = bytearray()
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
        print('Timeout Framing!')
        self.handle_fsm(None)
        
    def send(self, frame):          
        self._crc.clear()
        self._crc.update(frame)
        msg = self._crc.gen_crc()
        self._dev.write(b'~')    
        for i in range (len(msg)):
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
            self._state = self.idle
            self._idle(None)            
        elif self._state == self.idle:
            self._idle(byte)
        elif self._state == self.rx:
            self._rx(byte)
        elif self._state == self.esc:
            self._esc(byte)

    def _idle(self, byte):        
        if byte is None:
            self._received.clear()
            self._framesize = 0
            self.disable_timeout()            
        elif((byte == b'~') and (self._framesize == 0)):
            self._state = self.rx       
            self.enable_timeout()
        else:
            self._state = self.idle
            self.disable_timeout()

    def notifyLayer(self, data):
        self._top.receiveFromBottom(data)

    def _rx(self, byte):             
        if (self._framesize > self._bytes_max):
            self.disable_timeout()
            self._state = self.idle
            self._framesize = 0
            self._received.clear()
        elif(byte == b'~' and self._framesize >= self._bytes_min):            
            self._crc.clear()
            self._crc.update(self._received)
            if self._crc.check_crc():                
                self.notifyLayer(self._received[:self._framesize-2])
            self.disable_timeout()
            self._state = self.idle          
            self._framesize = 0            
            self._received.clear()            
        elif(byte == b'}'):
            self._state = self.esc
        elif(byte == b'~' and self._framesize == 0):
            self._state = self.rx
        elif (byte != b'~' or byte != b'}'):            
            self._received.append(int.from_bytes(byte, 'big'))
            self._framesize = self._framesize+1

    def _esc(self, byte):
       if(byte == b'~' or byte == b'}'):
           self._received.clear()
           self._framesize = 0
           self._state = self.idle
           self.disable_timeout()
       elif(byte == b'^'):
           self._received.append(int.from_bytes(b'~', 'big'))
           self._framesize = self._framesize + 1
           self._state = self.rx
       elif(byte == b']'):
           self._received.append(int.from_bytes(b'}', 'big'))
           self._framesize = self._framesize + 1
           self._state = self.rx
           
    def getDev(self):
        return self._dev

    def getRecebido(self):
        return self._received

    def getState(self):
        return self._state

