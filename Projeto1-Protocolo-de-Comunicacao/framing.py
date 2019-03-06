#!/usr/bin/python3

import serial, sys, enum

class Transmission():
    def __init__(self, dev):
        self.dev = dev
        self.estado = "ocioso"
        self.quadro = 0
    
    def handle(self, byte):
        print('>>>', self.getState())
        self.setState(byte)
    
    def _ocioso(self, byte):
        self.dev.write(byte)
        self.quadro = self.quadro + 1
        self.estado = "tx"
        
        
    def _tx(self, byte):
        if (byte == b'~' or byte == b'}') and (self.quadro < 5):
            self.dev.write(b'}')
            if byte == b'~':
                self.dev.write(b'^')
                self.quadro = self.quadro + 1
            else:
                self.dev.write(b']')
                self.quadro = self.quadro + 1

        elif (self.quadro < 6):
            self.dev.write(byte)
            self.quadro = self.quadro + 1
        else:
            self.estado = "ocioso"
    
    
   
    
    def setState(self, byte):
        if self.estado == "ocioso":
            self._ocioso(byte)
        elif self.estado == "tx":
            self._tx(byte)
      

    def getState(self):
        return self.estado
        

class Reception():
    def __init__(self, dev):
        #self.dev = dev
        #self.bytes_min = bytes_min
        #self.bytes_max = bytes_max
        self.estado = "ocioso"
        self.dev = dev
        self.quadro = 0
        self.recebido = []

    def  handle(self):
        print('>>>', self.getState())
        self.setState()

    def _ocioso(self):
        byte = self.dev.read()
        
        if((byte == b'~') and (self.quadro == 0)):
            self.estado = "rx"
        else:
            self.estado = "ocioso"

    def _rx(self):
        byte = self.dev.read()
        print ("Byte recebido: " + str(byte))
        if(byte == b'~' and self.quadro > 0):
            self.estado = "ocioso"
            self.quadro = 0
            self.recebido.clear()
            
            
        elif(byte == b'}'):
            self.estado = "esc"
        elif(byte == b'~' and self.quadro == 0):
            self.estado = "rx"
        elif (byte != b'~' or byte != b'}'):
            self.recebido.append(byte)
            self.quadro = self.quadro+1
        

    def _esc(self):
       byte = self.dev.read()
       print ("Byte recebido: " + str(byte))
       if(byte == b'~' or byte == b'}'):
           self.recebido.clear()
           self.quadro = 0
           self.estado = "ocioso"
       elif(byte == b'^' and self.quadro != 0):
           self.recebido.append(b'~')
           self.quadro = self.quadro + 1
           self.estado = "rx"
       elif(byte == b']' and self.quadro != 0):
           self.recebido.append(b'}')
           self.quadro = self.quadro + 1
           self.estado = "rx"
       else:
            self.estado = "rx"
    
    def getRecebido(self):
        return self.recebido

    def setState(self):
        if self.estado == "ocioso":
            self._ocioso()
        elif self.estado == "rx":
            self._rx()
        elif self.estado == "esc":
            self._esc()

    def getState(self):
        return self.estado

