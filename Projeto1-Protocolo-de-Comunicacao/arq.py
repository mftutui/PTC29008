#!/usr/bin/python3


import sys
import poller


class ARQ(poller.Layer):
    ACK0  = 0x80
    ACK1  = 0x88
    DATA0 = 0x00
    DATA1 = 0x08
    bytePROTOCOL = 0x00

    def __init__(self, obj, timeout):
        self._top = sys.stdin
        self._bottom = None
        self._state = False
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
        if self._state!= True:
            self._recvFromTOP = frame[:-1]
            self.sendToBottom()


    def handle_timeout(self):
        print ("Timeout!")
        if self._DATAN == False:
            print ("ACK0 não recebido. Reenviando mensagem 0")
            self.sendToBottom()
        elif self._DATAN == True:
            print ("ACK1 não recebido. Reenviando mensagem 1")
            self.sendToBottom()

    def sendToBottom(self):
        if self._DATAN == False:
            self.sendDataZero()
        elif self._DATAN == True :
            self.sendDataOne()
        self.enable_timeout()
        self._state = True
    
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

        elif self._state == True:
            if self._DATAN == False:
                if recvFromFraming[0] == self.ACK0:
                    print ("Receptor informou que recebeu a mensagem 0. Desabilitando timeout")
                    self.disable_timeout()
                    self._state = False
                    self._DATAN = not self._DATAN
                elif recvFromFraming[0] == self.ACK1:
                    print ("Receptor informou que recebeu a mensagem 1 porem ele deveria receber mensagem 0.")
                    self.sendDataZero()
                    self.enable_timeout()

            elif self._DATAN == True:
                if recvFromFraming[0] == self.ACK1:
                    print ("Receptor informou que receboe a mensagem 1. Desabilitando timeout")
                    self.disable_timeout()
                    self._state = False
                    self._DATAN = not self._DATAN

                elif recvFromFraming[0] == self.ACK0:
                    print ("Receptor informou que recebeu a mensagem 0 porem ele deveria receber mensagem 1.")
                    self.sendDataOne()
                    self.enable_timeout()