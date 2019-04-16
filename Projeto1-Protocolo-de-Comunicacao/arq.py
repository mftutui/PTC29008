#!/usr/bin/python3


import sys
import poller
import random


class ARQ(poller.Layer):
    ACK0  = 0x80
    ACK1  = 0x88
    DATA0 = 0x00
    DATA1 = 0x08
    bytePROTOCOL = 0x00
    timeSlot = .1

    def __init__(self, obj, timeout):
        self._top = sys.stdin
        self._bottom = None
        self._state = 0
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = obj
        self.disable_timeout()
        self._expDATA = False
        self._recvFromTOP = None
        self._DATAN = False
    
    def sendACK0(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.ACK0)
        frameToBeSent.append(self.bytePROTOCOL)
        self.sendToLayer(frameToBeSent)
    
    def sendACK1(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.ACK1)
        frameToBeSent.append(self.bytePROTOCOL)
        self.sendToLayer(frameToBeSent)


    def sendDataZero(self,):
        print ("Enviando mensagem 0")
        frameToBeSent = bytearray()
        frameToBeSent.append(self.DATA0)
        frameToBeSent.append(self.bytePROTOCOL)
        for i in range (len(self._recvFromTOP)):
            frameToBeSent.append(int.from_bytes(self._recvFromTOP[i].encode('ascii'),'big'))
            
        self.sendToLayer(frameToBeSent)
  


    def sendDataOne(self):
        print ("Enviando mensagem 1")
        frameToBeSent = bytearray()
        frameToBeSent.append(self.DATA1)
        frameToBeSent.append(self.bytePROTOCOL)
        for i in range (len(self._recvFromTOP)):
            frameToBeSent.append(int.from_bytes(self._recvFromTOP[i].encode('ascii'),'big'))
        self.sendToLayer(frameToBeSent)
    


    def setBottom(self, bottom):
        self._bottom = bottom


    def sendToLayer(self, frameToBeSent):
        self._bottom.send(frameToBeSent)
        
        

    def handle(self):
        frame = sys.stdin.readline()
        if self._state == 0 :
            self._recvFromTOP = frame[:-1]
            self.sendToBottom()
            self._state = 1
            self.reload_timeout()
            self.enable_timeout()

    def handle_timeout(self):

        self.arqTimeoutHandler()
        


    def arqTimeoutHandler(self):

        if (self._state == 1):
            print ("Estouro de timeout!")
            print("Estado ao estourar timeout:", self._state)
            backoff = self.generateBackoff()
            if(backoff == 0):
                self.sendToBottom()
                self.reload_timeout()
                self.enable_timeout()
            else:
                self._state = 3
                self.changeTimeoutValue(int(backoff*self.timeSlot))
        elif (self._state == 2):
            print ("Estouro de backoff")
            print("Estado ao estourar o backoff:", self._state)
            self._state = 0
            self.reload_timeout()
            self.disable_timeout()
        elif (self._state == 3):
            print ("Estouro de backoff")
            print ("Estado ao estourar o backoff:", self._state)
            self.sendToBottom()
            self.reload_timeout()
            self._state = 1
        print("Estado atual:", self._state)
        print("Timeout atual:", self.timeout)
        print('\n')
            


    def sendToBottom(self):
        if self._DATAN == False:
            self.sendDataZero()
        elif self._DATAN == True :
            self.sendDataOne()
 
        
    
    def generateBackoff(self):
        return random.randint(80,80)

    def changeTimeoutValue(self, timeout):
        self.timeout = timeout

    def receiveFromBottom(self, recvFromFraming):
        if recvFromFraming[0] == self.DATA0:
            if self._expDATA == False:
                print ("Mensagem 0 recebida:")
                print(recvFromFraming[2:].decode('ascii'))
                self._expDATA = True
                self.sendACK0()                        
            elif self._expDATA == True:
                self.sendACK0()
                
        elif recvFromFraming[0] == self.DATA1:
            if self._expDATA == True:
                print ("Mensagem 1 recebida:")
                print(recvFromFraming[2:].decode('ascii'))
                self._expDATA = False
                self.sendACK1()
            elif self._expDATA == False:
                self.sendACK1()

        elif self._state == 1:
            if self._DATAN == False:
                if recvFromFraming[0] == self.ACK0:
                    print ("Receptor informou que recebeu a mensagem 0. Entrando no backoff")
                    self._DATAN = not self._DATAN
                    backoff = self.generateBackoff()
                    if (backoff == 0):
                        self._state = 0
                        self.disable_timeout()
                    else:
                        self._state = 2
                        self.changeTimeoutValue(backoff*self.timeSlot)
                        self.enable_timeout()

                elif recvFromFraming[0] == self.ACK1:
                    print ("Receptor informou que recebeu a mensagem 1 porem ele deveria receber mensagem 0.")
                    backoff = self.generateBackoff()
                    if(backoff == 0):
                        self.sendDataZero()
                        self.reload_timeout()
                        self.enable_timeout()
                    else:
                        self._state = 3
                        self.changeTimeoutValue(backoff*self.timeSlot)
                        self.enable_timeout()
                  

            elif self._DATAN == True:
                if recvFromFraming[0] == self.ACK1:
                    print ("Receptor informou que recebeu a mensagem 1. Entrando no backoff")
                    self._DATAN = not self._DATAN
                    backoff = self.generateBackoff()
                    if (backoff == 0):
                        self._state = 0
                        self.disable_timeout()
                    else:
                        self._state = 2
                        self.changeTimeoutValue(backoff*self.timeSlot)
                        self.enable_timeout()

                elif recvFromFraming[0] == self.ACK0:
                    print ("Receptor informou que recebeu a mensagem 0 porem ele deveria receber mensagem 1.")
                    backoff = self.generateBackoff()
                    if(backoff == 0):
                        self.sendDataOne()
                        self.reload_timeout()
                        self.enable_timeout()
                    else:
                        self._state = 3
                        self.changeTimeoutValue(backoff*self.timeSlot)
                        self.enable_timeout()