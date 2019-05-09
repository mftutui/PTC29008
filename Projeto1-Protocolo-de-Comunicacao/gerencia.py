#!/usr/bin/python3
# -*- coding: utf-8 -*- 

'''
    Gerenciamento de sessão
'''

import layer
import sys
import os
class GER(layer.Layer):
    '''
    Classe responsável por estabelecer, manter e finalizar
    uma conexão
    '''
    DISC = 0
    HAND1 = 1
    HAND2 = 2
    CONN = 3
    CHECK = 4
    HALF1 = 5
    HALF2 = 6
    byteGER = 0xFF
    byteDATA = 0x00
    CR = 0x00
    CC = 0x01
    KR = 0x02
    KC = 0x03
    CA = 0x07
    DR = 0x04
    DC = 0x05
    checkInterval = 5    
    
    def __init__(self, fd, id, timeout):
        ''' fd: descritor de arquivos da classe
            id: id da sessão
            timeout: timeout: intervalo de tempo para interrupção interna
        '''
        self.fd = fd
        self.timeout = timeout
        self.base_timeout = timeout
        self._top = None
        self._bottom = None
        self._gerID = id
        self.enable()
        self.disable_timeout()
        self._state = self.DISC
        self._initialTimeout = timeout
        self._retries = 0
        self._isConn = False
    
    def changeTimeoutValue(self, timeout):
        ''' Altera o valor do timeout do objeto
            timeout: novo valor do timeout
        '''
        self.base_timeout = timeout 

    def disconRequest(self):
        ''' Monta o quadro com a mensagem de solicitação desconexão
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.DR)
        self.sendToLayer(frameToBeSent)

    def disconConfirm(self):
        '''  Monta o quadro com a mensagem de confirmação de desconexão
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.DC)
        self.sendToLayer(frameToBeSent)

    def connRequest(self):
        ''' Monta o quadro com a mensagem de solicitação de conexão
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CR)
        self.sendToLayer(frameToBeSent)
        self._state = self.HAND1
        self.enable_timeout()
    
    def connConfirm(self):
        ''' Monta o quadro com a mensagem de confirmação de conexão
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CC)
        self.sendToLayer(frameToBeSent)
    
    def keepAliveRequest(self):
        ''' Monta o quadro com a mensagem keep-alive
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.KR)
        self._state = self.CHECK
        self.sendToLayer(frameToBeSent)
        self.changeTimeoutValue(self._initialTimeout)
        self._reloadAndEnableTimeout()
    
    def keepAliveConfirm(self):
        ''' Monta o quadro com a mensagem de confirmação de keep-alive
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.KC)
        self.sendToLayer(frameToBeSent)

    def connAccepted(self):
        ''' Monta o quadro com a mensagem de ACK de conexão
        '''
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CA)
        self.sendToLayer(frameToBeSent) 

    def setBottom(self, bottom):
        ''' Método para definir camada inferior da classe arq
            bottom: objeto da camada inferior
        '''
        self._bottom = bottom

    def setTop(self, top):
        ''' Método para definir camada superior da classe arq
            top: objeto da camada superior
        '''
        self._top = top

    def notifyError(self):
        ''' Método que indica que houve erro fatal na comunicação
        '''
        self.goToDisc()
    
    def receiveFromTop(self, data):
        ''' Envia o quadro de dados para a camada inferior
            data: bytearray representando o quadro a ser enviado
        '''   
        if(self._state == self.CONN or self._state == self.CHECK):
            if (len(data) > 0):  
                data.insert(0, self.byteDATA)
                data.insert(0, self._gerID)
                self.sendToLayer(data)  

    def handle(self):
        pass 

    def goToDisc(self):
        ''' Configura a máquina de estados da classe para o estado
            desconectado
        '''
        self._state = self.DISC
        self._retries = 0
        self.changeTimeoutValue(self._initialTimeout)
        self._reloadAndEnableTimeout()
        self._isConn = False
        os.system('clear')
        print("Verifique se a outra estação está ativa")

    def handle_timeout(self):
        ''' Trata a interrupção interna devido ao timeout
        '''            
        if(self._state == self.HAND1):
            if(self._retries < 3):
                self.connRequest()
                self._retries = self._retries + 1
            else:
                self.goToDisc()
        elif(self._state == self.HAND2):
            self.goToDisc()        
        elif(self._state == self.CONN):
            self.keepAliveRequest()         
        elif(self._state == self.CHECK):
            if (self._retries < 3):                
                self._retries = self._retries + 1
                self.keepAliveRequest()
            else:
                self.goToDisc()
        elif(self._state == self.HALF1):
            if(self._retries < 3):
                self._retries = self._retries + 1
                self.disconRequest()
            else:
                self.goToDisc()
        elif(self._state == self.HALF2):
            self.goToDisc()           

    def sendToLayer(self, data):
        ''' Envia o frame a ser transmitido para a camada inferior
            data: bytearray representando o frame a ser transmitido
        ''' 
        self._bottom.receiveFromTop(data)

    def receiveFromBottom(self, data):
        ''' Recebe um quadro da camada inferior
            data: bytearray representando o quadro recebido
        ''' 
        self.handle_fsm(data)

    def notifyLayer(self, data):
        ''' Envia o frame recebido para a camada superior
            data: bytearray representando o frame a ser enviado
        ''' 
        self._top.receiveFromBottom(data)
    
    def _reloadAndEnableTimeout(self):
        self.reload_timeout()
        self.enable_timeout()

    def _disc(self, data):
        if (data[1] == self.CR and data[0] == self.byteGER):
            self.connConfirm()
            self._state = self.HAND2
            self.changeTimeoutValue(self._initialTimeout)
            self._reloadAndEnableTimeout()

    def _hand1(self, data):
        if (data[1] == self.CR and data[0] == self.byteGER):
            self._retries = 0
            self.connConfirm()
        elif (data[1] == self.CC and data[0] == self.byteGER):
            self._state = self.CONN
            self._retries = 0
            #self._botton._state = 0
            self.connAccepted()
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()            
        elif (data[1] == self.CA and data[0] == self.byteGER):
            self._state = self.CONN
            self._retries = 0
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()

    def _hand2(self,data):
        if (data[1] == self.CA and data[0] == self.byteGER):
            self._retries = 0
            self._state = self.CONN
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()
        elif(data[1] == self.DR and data[0] == self.byteGER):
            self._retries = 0
            self.disconRequest()
            self._state = self.HALF2
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()
        else:
            self._retries = 0
            self.notifyLayer(data[1:])
            self._state = self.CONN
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()

    def _conn(self, data):
        if(data[1] == self.CR and data[0] == self.byteGER):
            self.connConfirm()
        elif(data[1] == self.KR and data[0] == self.byteGER):
            self.keepAliveConfirm()
        elif(data[1] == self.DR and data[0] == self.byteGER):
            self.disconRequest()
            self._state = self.HALF2
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()
        else:
            self.notifyLayer(data[1:])
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()

    def _check(self, data):
        if(data[1] == self.KR and data[0] == self.byteGER):
            self.keepAliveConfirm()
        elif(data[1] == self.KC and data[0] == self.byteGER):
            self._state = self.CONN
            self._retries = 0
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()
        elif(data[1] == self.DR and data[0] == self.byteGER):
            self.disconRequest()
            self._retries = 0
            self._state = self.HALF2
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()               
        else:
            self.notifyLayer(data[1:])
            self._state = self.CONN
            self._retries = 0
            self.changeTimeoutValue(self.checkInterval)
            self._reloadAndEnableTimeout()

    def _half1(self, data):
        if (data[1] == self.DR and data[0] == self.byteGER):
            self.disconConfirm()
            self.goToDisc()
        elif (data[1] == self.KR and data[0] == self.byteGER):
            self.disconRequest
            self._retries = 0
        else:
            self._retries = 0
            self.notifyLayer(data[1:])

    def _half2(self, data):
        if(data[1] == self.DR and data[0] == self.byteGER):
            self.disconRequest()
            self._retries = 0
        elif (data[1] == self.DC):
            self.goToDisc()

    def handle_fsm(self, data):

      
        ''' Recebe um quadro e faz o tratamento na máquina de estados 
            da classe
            data: bytearray representando o frame a ser enviado
        '''    
        if (self._state == self.DISC):
            self._disc(data)
        elif (self._state == self.HAND1):
            self._hand1(data)   
        elif (self._state == self.HAND2):
            self._hand2(data)           
        elif (self._state == self.CONN):
            self._conn(data)       
        elif(self._state == self.CHECK):
            self._check(data) 
        elif (self._state == self.HALF1):
            self._half1(data)
        elif (self._state == self.HALF2):
            self._half2(data)
        if(self._state == self.CONN and self._isConn == False):
            os.system('clear')
            print("Estação pronta para troca de dados")
            self._isConn = True