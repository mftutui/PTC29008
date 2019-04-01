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
        self.flag = 0
    
    def sendACK0(self):
        quadro_aux = bytearray()
        quadro_aux.append(self.ack_0)
        quadro_aux.append(self.protocolo)
        self.sendToLayer(quadro_aux)
    
    def sendACK1(self):
        quadro_aux = bytearray()
        quadro_aux.append(self.ack_1)
        quadro_aux.append(self.protocolo)
        self.sendToLayer(quadro_aux)
         



    def montaQuadroZero(self,dado):
        quadro_aux = bytearray()
        quadro_aux.append(self.dado_0)
        quadro_aux.append(self.protocolo)
        for i in range (len(dado)):
            quadro_aux.append(int.from_bytes(dado[i].encode('ascii'),'big'))
            
        self.sendToLayer(quadro_aux)
        print ("saiu do monta")       
        

    def setBottom(self, bottom):
        self._bottom = bottom

    def sendToLayer(self, dados):       
        self._bottom.send(dados)
        
        

    def handle(self):
        quadro = sys.stdin.readline()
        if self.flag != 1:
            
            self._dado = quadro[:-1]
            self.handle_fsm(quadro[:-1])
            self.flag = 1
            self.enable_timeout()
            print ("habilitou timeout")
        
      
    
    def montaQuadroOne(self, dado):        
        quadro_aux = bytearray()
        quadro_aux.append(self.dado_1)
        quadro_aux.append(self.protocolo)
        for i in range (len(dado)):
            quadro_aux.append(int.from_bytes(dado[i].encode('ascii'),'big'))
            
        self.sendToLayer(quadro_aux) 
        print ("saiu do monta")       
               
       

    def _stateZero(self, quadro):
            print("entrou func zero")
            self.montaQuadroZero(quadro)   
                     
            
           
    
    def _stateOne(self, quadro):
            print("entrou func1")
            self.montaQuadroOne(quadro)
            
            
           

    def handle_fsm(self,quadro):
        
        if self._state == False:
            self._stateZero(quadro)
        elif self._state == True:
            self._stateOne(quadro)

    def handle_timeout(self):
        
        print ("ACK NÃO RECEBIDO...")
        print ("Enviando:", self._dado)

        if self._state == False:
            self.montaQuadroZero(self._dado)
        elif self._state == True:
            self.montaQuadroOne(self._dado)
        
    
    def receiveFromBottom(self, dados):
        if dados[0] == self.dado_0:
            if self.M == 0:
                print(dados[2:].decode('ascii'))
                self.M = 1
                self.sendACK0()               
            elif self.M == 1:
                self.sendACK0()
                
        elif dados[0] == self.dado_1:
            if self.M == 1:
                print(dados[2:].decode('ascii'))
                self.M = 0
                self.sendACK1()
            elif self.M == 0:
                self.sendACK1()

        elif dados[0] == self.ack_0:
            if self._state == False:
                print("ack 0 recebido ")
                self.disable_timeout()
                print("timeout desabilitado")
                self.flag = 0
                self._state = True
            elif self._state == True:
                self.montaQuadroOne(self._dado)
               
        
        elif dados[0] == self.ack_1:
            if self._state == True:
                print("ack 1 recebido ")
                self.disable_timeout()
                print("timeout desabilitade")                
                self._state = False
                self.flag = 0
            elif self._state == False:                
                self.montaQuadroZero(self._dado)
              

