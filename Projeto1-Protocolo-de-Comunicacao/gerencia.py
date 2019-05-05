import layer
import sys
import signal


class GER(layer.Layer):
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
        self.fd = fd
        self.timeout = timeout
        self.base_timeout = timeout
        self._top = None
        self._bottom = None
        self._gerID = 0xFE
        self.enable()
        self.disable_timeout()
        self._state = self.DISC
        self._initialTimeout = timeout
        self._retries = 0
    
    def changeTimeoutValue(self, timeout):
        self.base_timeout = timeout 

    def disconRequest(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.DR)
        self.sendToLayer(frameToBeSent)

    def disconConfirm(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.DC)
        self.sendToLayer(frameToBeSent)

    def connRequest(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CR)
        self.sendToLayer(frameToBeSent)
        self._state = self.HAND1
        self.enable_timeout()
    
    def connConfirm(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CC)
        self.sendToLayer(frameToBeSent)
    
    def keepAliveRequest(self):
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
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.KC)
        self.sendToLayer(frameToBeSent)

    def connAccepted(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self._gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CA)
        self.sendToLayer(frameToBeSent) 

    def setBottom(self, bottom):
        self._bottom = bottom

    def setTop(self, top):
        self._top = top

    def notifyError(self):
        self.goToDisc()
    
    def receiveFromTop(self, data):
        if(self._state == self.CONN or self._state == self.CHECK):  
            data.insert(0, self.byteDATA)
            data.insert(0, self._gerID)
            self.sendToLayer(data)  

    def handle(self):
        pass 

    def goToDisc(self):
        self._state = self.DISC
        self._retries = 0
        self.changeTimeoutValue(self._initialTimeout)
        self.reload_timeout()
        self.disable_timeout()
        print ("Estado GER", self._state) 

    def handle_timeout(self):        
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
        self._bottom.receiveFromTop(data)

    def receiveFromBottom(self, recvFromARQ):
       self.handle_fsm(recvFromARQ)

    def notifyLayer(self, data):
        self._top.receiveFromBottom(data)

    def handle_fsm(self, recvFromARQ):    
        if (self._state == self.DISC):
            if (recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                self.connConfirm()
                self._state = self.HAND2
                self.enable_timeout()
        elif (self._state == self.HAND2):
            if (recvFromARQ[1] == self.CA and recvFromARQ[0] == self.byteGER):
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
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()   
                self.enable_timeout()   
                self.connAccepted()          
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
                self._retries = 0
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
                self.disconRequest
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

  
            
