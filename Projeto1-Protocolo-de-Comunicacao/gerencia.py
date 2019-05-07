    #!/usr/bin/python3
    # -*- coding: utf-8 -*- 

'''
    Gerenciamento de sessão
'''

import layer
import sys


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
        self.reload_timeout()
        self.enable_timeout()
    
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
        self.reload_timeout()
        self.disable_timeout()        
        print ("Estado GER", self._state) 

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
            print ("Erro hand2")
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

    def receiveFromBottom(self, recvFromARQ):
        ''' Recebe um quadro da camada inferior
            recvFromARQ: bytearray representando o quadro recebido
        ''' 
        self.handle_fsm(recvFromARQ)

    def notifyLayer(self, data):
        ''' Envia o frame recebido para a camada superior
            data: bytearray representando o frame a ser enviado
        ''' 
        self._top.receiveFromBottom(data)

    def _disc(self, recvFromARQ):
        if (recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
            self.connConfirm()
            self._state = self.HAND2
            self.changeTimeoutValue(self._initialTimeout)
            self.reload_timeout()   
            self.enable_timeout()
           

    def handle_fsm(self, recvFromARQ):
        #print("Quadro recebido no gerenciamento", recvFromARQ)
      
        ''' Recebe um quadro e faz o tratamento na máquina de estados 
            da classe
            recvFromARQ: bytearray representando o frame a ser enviado
        '''    
        if (self._state == self.DISC):
            self._disc(recvFromARQ)
        elif (self._state == self.HAND2):
            if (recvFromARQ[1] == self.CA and recvFromARQ[0] == self.byteGER):
                #print("Recebeu CA")
                self._retries = 0
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()   
                self.enable_timeout()
            elif(recvFromARQ[1] == self.DR and recvFromARQ[0] == self.byteGER):
                self._retries = 0
                self.disconRequest()
                self._state = self.HALF2
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
            else:
                print(recvFromARQ)
                #print("Recebeu CA")
                self._retries = 0
                self.notifyLayer(recvFromARQ[1:])
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
        elif (self._state == self.HAND1):
            if (recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                self._retries = 0
                self.connConfirm()
            elif (recvFromARQ[1] == self.CC and recvFromARQ[0] == self.byteGER):
                self._state = self.CONN
                self._retries = 0
                self._bottom._state = 0
                self.connAccepted()
                #print ("enviando ca", self._bottom._state)
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()   
                self.enable_timeout()             
            elif (recvFromARQ[1] == self.CA and recvFromARQ[0] == self.byteGER):
                self._state = self.CONN
                self._retries = 0
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()              
        elif (self._state == self.CONN):
            if(recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                self.connConfirm()
            elif(recvFromARQ[1] == self.KR and recvFromARQ[0] == self.byteGER):
                self.keepAliveConfirm()
            elif(recvFromARQ[1] == self.DR and recvFromARQ[0] == self.byteGER):
                self.disconRequest()
                self._state = self.HALF2
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
            else:
                self.notifyLayer(recvFromARQ[1:])
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()        
        elif(self._state == self.CHECK):
            if(recvFromARQ[1] == self.KR and recvFromARQ[0] == self.byteGER):
                self.keepAliveConfirm()
                self._retries = 0
            elif(recvFromARQ[1] == self.KC and recvFromARQ[0] == self.byteGER):
                self._state = self.CONN
                self._retries = 0
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
            elif(recvFromARQ[1] == self.DR and recvFromARQ[0] == self.byteGER):
                self.disconRequest()
                self._retries = 0
                self._state = self.HALF2
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()                
            else:
                self.notifyLayer(recvFromARQ[1:])
                self._state = self.CONN
                self._retries = 0
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout() 
        elif (self._state == self.HALF1):
            if (recvFromARQ[1] == self.DR and recvFromARQ[0] == self.byteGER):
                self.disconConfirm()
                self.goToDisc()
            elif (recvFromARQ[1] == self.KR and recvFromARQ[0] == self.byteGER):
                self.disconRequest()
                self._retries = 0
            else:
                self._retries = 0
                self.notifyLayer(recvFromARQ[1:])
        elif (self._state == self.HALF2):
            if(recvFromARQ[1] == self.DR and recvFromARQ[0] == self.byteGER):
                self.disconRequest()
                self._retries = 0
            elif (recvFromARQ[1] == self.DC):
                self.goToDisc()
        print("Estado atual GER:", self._state)