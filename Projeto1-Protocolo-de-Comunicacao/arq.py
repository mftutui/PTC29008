#!/usr/bin/python3
# -*- coding: utf-8 -*- 

'''
    ARQ 
'''

import sys
import poller
import layer
import random


class ARQ(layer.Layer):
    '''
    Classe responsável por garantir a entrega de quadros
    e controlar o acesso ao meio
    '''
    ACK0  = 0x80
    ACK1  = 0x88
    DATA0 = 0x00
    DATA1 = 0x08
    bytePROTOCOL = 0x00
    timeSlot = .1

    def __init__(self, fd, timeout):
        ''' fd: descritor de arquivos da classe
            timeout: intervalo de tempo para interrupção interna
        '''
        self._top = None
        self._bottom = None
        self._state = 0
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = fd
        self.disable_timeout()
        self._expDATA = False
        self._recvFromTOP = bytearray()
        self._DATAN = False
        self._initialTimeout = timeout
        self.enable()
        self._retries = 0
    
    def sendACK0(self):
        ''' Envia o quadro de ACK da mensagem 0
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self.ACK0)        
        frameToBeSent.append(self._top._gerID)
        self.sendToLayer(frameToBeSent)
    
    def sendACK1(self):
        ''' Envia o quadro de ACK da mensagem 1
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self.ACK1)
        frameToBeSent.append(self._top._gerID)
        self.sendToLayer(frameToBeSent)

    def sendDataZero(self):
        ''' Envia o quadro da mensagem 0
        '''
        frameToBeSent = bytearray()
        frameToBeSent = self._recvFromTOP
        if (frameToBeSent[0] is not self.DATA0):
            frameToBeSent.insert(0, self.DATA0)
        self.sendToLayer(frameToBeSent)
        

    def sendDataOne(self):
        ''' Envia o quadro da mensagem 1 
        '''
        frameToBeSent = bytearray()
        frameToBeSent = self._recvFromTOP
        if(frameToBeSent[0] is not self.DATA1):
            frameToBeSent.insert(0,self.DATA1)
        self.sendToLayer(frameToBeSent)  

    def setTop(self, top):
        ''' Método para definir camada superior da classe arq
            top: objeto da camada superior
        '''
        self._top = top

    def setBottom(self, bottom):
        ''' Método para definir camada inferior da classe arq
            bottom: objeto da camada inferior
        '''
        self._bottom = bottom


    def sendToLayer(self, frameToBeSent):
        ''' Envia o frame a ser transmitido para a camada inferior
            frameToBeSent: bytearray representando o frame a ser transmitido
        '''  
        print("Quadro sendo enviado pelo ARQ", frameToBeSent)
        self._bottom.receiveFromTop(frameToBeSent)       
        

    def receiveFromTop(self, data):
        ''' Envia o quadro de dados para a camada inferior
            data: bytearray representando o quadro a ser enviado
        '''   
        if self._state == 0 :
            self._recvFromTOP.clear()
            self._recvFromTOP = data
            self.sendToBottom()
            self._state = 1
            self.changeTimeoutValue(self._initialTimeout)
            self.reload_timeout()
            self.enable_timeout()
            self._top.disable()
            self._retries = 0

    def handle(self):
        pass

    def handle_timeout(self):
        self.arqTimeoutHandler()       

    def arqTimeoutHandler(self):
        ''' Trata a interrupção interna devido ao timeout
        '''      
        if (self._state == 1):
            if (self._retries < 3):
                self._retries = self._retries + 1
                backoff = self.generateBackoff()
                if(backoff == 0):
                    self.sendToBottom()
                    self.changeTimeoutValue(self._initialTimeout)
                    self.reload_timeout()
                    self.enable_timeout()
                else:
                    self._state = 3
                    self.changeTimeoutValue(int(backoff*self.timeSlot))
                    self.reload_timeout()
                    self.enable_timeout()
            else:
                self._retries = 0 
                self._state = 0
                self._DATAN = False
                self._expDATA = False
                print ("Erro arq")
                self._top.notifyError()
                self.changeTimeoutValue(self._initialTimeout)
                self.disable_timeout()
                self._top.enable()
        elif (self._state == 2):
            self._state = 0
            self._retries = 0
            self.changeTimeoutValue(self._initialTimeout)
            self.disable_timeout()
            self._top.enable()
        elif (self._state == 3):
            self.sendToBottom()
            self._state = 1   
            self.changeTimeoutValue(self._initialTimeout)
            self.reload_timeout()
            self.enable_timeout()
                

    def sendToBottom(self):
        ''' Verifica qual mensagem (0 ou 1) será enviada
        '''
        if self._DATAN == False:
            self.sendDataZero()
        elif self._DATAN == True :
            self.sendDataOne()
        
    def generateBackoff(self):
        ''' Gera um numero inteiro para gerar um backoff
        '''
        return random.randint(0,7)

    def changeTimeoutValue(self, timeout):
        ''' Altera o valor do timeout do objeto
            timeout: novo valor do timeout
        '''
        self.base_timeout = timeout
    
    def disableBackoff(self):
        ''' Desabilita o backoff do objeto
        '''        
        if(self._state == 2 or self._state == 3):  
            self.disable_timeout()
            if self._state == 2:
                self._state = 0
                self._retries = 0
                self.changeTimeoutValue(self._initialTimeout)
                self.reload_timeout()
                self.disable_timeout()
                self._top.enable()
            elif self._state == 3:
                self._state = 1
                self.sendToBottom()                
                self.changeTimeoutValue(self._initialTimeout)
                self.reload_timeout()
                self.enable_timeout()

    def notifyLayer(self, data):
        ''' Envia o frame recebido para a camada superior
            data: bytearray representando o frame a ser enviado
        ''' 
        self._top.receiveFromBottom(data)

    def receiveFromBottom(self, recvFromFraming):
        print("Quadro recebido no arq", recvFromFraming)
        ''' Recebe um quadro da camada inferior
            recvFromFraming: bytearray representando o quadro recebido
        ''' 
        if(recvFromFraming[1] == self._top._gerID):
            if recvFromFraming[0] == self.DATA0:
                if self._expDATA == False:                    
                    self._expDATA = True
                    self.sendACK0() 
                    self.notifyLayer(recvFromFraming[2:]) 
                    self.disableBackoff()                                       
                elif self._expDATA == True:
                    self.sendACK0()
                    self.disableBackoff()                    
            elif recvFromFraming[0] == self.DATA1:
                if self._expDATA == True:                    
                    self._expDATA = False
                    self.sendACK1()
                    self.notifyLayer(recvFromFraming[2:])  
                    self.disableBackoff()                                      
                elif self._expDATA == False:
                    self.sendACK1()
                    self.disableBackoff()
            elif self._state == 1:
                if self._DATAN == False:
                    if recvFromFraming[0] == self.ACK0:
                        self._retries = 0
                        self._DATAN = not self._DATAN
                        backoff = self.generateBackoff()
                        if (backoff == 0):
                            self._state = 0
                            self.disable_timeout()
                            self._top.enable()
                        else:
                            self._state = 2
                            self.changeTimeoutValue(int(backoff*self.timeSlot))
                            self.reload_timeout()
                            self.enable_timeout()
                    elif recvFromFraming[0] == self.ACK1:
                        backoff = self.generateBackoff()
                        if(backoff == 0):
                            self.sendDataZero()
                            self.changeTimeoutValue(self._initialTimeout)
                            self.reload_timeout()
                            self.enable_timeout()
                        else:
                            self._state = 3
                            self.changeTimeoutValue(int(backoff*self.timeSlot))
                            self.reload_timeout()
                            self.enable_timeout()                  
                elif self._DATAN == True:
                    if recvFromFraming[0] == self.ACK1:
                        self._retries = 0
                        self._DATAN = not self._DATAN
                        backoff = self.generateBackoff()
                        if (backoff == 0):
                            self._state = 0
                            self.disable_timeout()
                            self._top.enable()
                        else:
                            self._state = 2
                            self.changeTimeoutValue(int(backoff*self.timeSlot))
                            self.reload_timeout()
                            self.enable_timeout()                        
                    elif recvFromFraming[0] == self.ACK0: 
                        backoff = self.generateBackoff()
                        if(backoff == 0):
                            self.sendDataOne()
                            self.changeTimeoutValue(self._initialTimeout)
                            self.reload_timeout()
                            self.enable_timeout()
                        else:
                            self._state = 3
                            self.changeTimeoutValue(int(backoff*self.timeSlot))
                            self.reload_timeout()
                            self.enable_timeout()