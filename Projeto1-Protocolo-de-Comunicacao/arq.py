#!/usr/bin/python3


import serial, sys, enum
import poller
import crc

class ARQ(poller.Layer):
    ack_0  = 0x80
    ack_1  = 0x88
    dado_0 = 0x00
    dado_1 = 0x08
    protocolo = 0x00

    def __init__(self, obj, timeout):
        self._top = sys.stdin
        self._bottom = None
        self._state = False        
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = obj
        self.disable_timeout()
        self.N = 0
        self.M = 0
        self._quadro = bytearray()
        self._dado = None

        

    def setBottom(self, bottom):
        self._bottom = bottom

    def sendToLayer(self, dados):       
        self._bottom.send(dados)
        
        

    def handle(self):
        quadro = sys.stdin.readline()
        self._dado = quadro[:-1]
        self.handle_fsm(quadro[:-1])
      
    
    def montaQuadro(self, dado):
        print(self._state)
        self._quadro.clear()
        if self._state == False:
            
            self._quadro.append(self.dado_0)
            self._quadro.append(self.protocolo)
            for i in range (len(dado)):
                self._quadro.append(int.from_bytes(dado[i].encode('ascii'),'big'))
            
            self.sendToLayer(self._quadro)
          
            
        
        elif self._state == True:            
            self._quadro.append(self.dado_1)
            self._quadro.append(self.protocolo)
            for i in range (len(dado)):
                self._quadro.append(int.from_bytes(dado[i].encode('ascii'),'big'))
            
            self.sendToLayer(self._quadro)
        
        self.enable_timeout()        
        print("timeout habilitade")

    def _stateZero(self, quadro):
            self.montaQuadro(quadro)   
                     
            
           
    
    def _stateOne(self, quadro):
            self.montaQuadro(quadro)
            
            
           

    def handle_fsm(self,quadro):
        
        if self._state == False:
            self._stateZero(quadro)
        elif self._state == True:
            self._stateOne(quadro)

    def handle_timeout(self):
        
        print ("ACK NÃO RECEBIDO...")
        print ("Enviando ", self._dado)
        self.montaQuadro(self._dado)
    
    def receiveFromBottom(self, dados):
        if dados[0] == self.dado_0:
            if self.M == 0:
                print(dados[2:].decode('ascii'))
                self.M = 1
                quadro_aux = bytearray()
                quadro_aux.append(self.ack_0)
                quadro_aux.append(self.protocolo)                
                self.sendToLayer(quadro_aux)
               
            elif self.M == 1:
                quadro_aux = bytearray()
                quadro_aux.append(self.ack_0)
                quadro_aux.append(self.protocolo)                
                self.sendToLayer(quadro_aux)
                
        elif dados[0] == self.dado_1:
            if self.M == 1:
                print(dados[2:].decode('ascii'))
                self.M = 0
                quadro_aux = bytearray()
                quadro_aux.append(self.ack_1)
                quadro_aux.append(self.protocolo)                
                self.sendToLayer(quadro_aux)
            elif self.M == 0:
                quadro_aux = bytearray()
                quadro_aux.append(self.ack_1)
                quadro_aux.append(self.protocolo)                
                self.sendToLayer(quadro_aux)
        elif dados[0] == self.ack_0:
            if self._state == False:
                print("ack 0 recebido ")
                self.disable_timeout()
                print("timeout desabilitade")
                self._quadro.clear()
                self._state = True
            elif self._state == True:
                quadro_aux = bytearray()
                quadro_aux.append(self.dado_0)
                quadro_aux.append(self.protocolo)
                for i in range (len(self._dado)):
                    quadro_aux.append(int.from_bytes(self._dado[i].encode('ascii'),'big'))
                self.sendToLayer(quadro_aux)
        
        elif dados[0] == self.ack_1:
            if self._state == True:
                print("ack 1 recebido ")
                self.disable_timeout()
                print("timeout desabilitade")
                self._quadro.clear()
                self._state = False
                
            elif self._state == False:                
                quadro_aux = bytearray()
                quadro_aux.append(self.dado_1)
                quadro_aux.append(self.protocolo)
                for i in range (len(self._dado)):
                    quadro_aux.append(int.from_bytes(self._dado[i].encode('ascii'),'big'))
                self.sendToLayer(quadro_aux)
              

