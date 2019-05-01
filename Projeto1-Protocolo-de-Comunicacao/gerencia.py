import layer
import sys

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
    gerID = 0xFE
    CR = 0x00
    CC = 0x01
    KR = 0x02
    KC = 0x03
    CA = 0x07
    DR = 0x04
    checkInterval = 15

    def __init__(self, fd, timeout):
        self.fd = fd
        self.timeout = timeout
        self.base_timeout = timeout
        self._top = None
        self._bottom = None
        self.enable()
        self.disable_timeout()
        self._state = self.DISC
        self._initialTimeout = timeout

    
    def changeTimeoutValue(self, timeout):
           self.base_timeout = timeout 

    def connRequest(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CR)
        self.sendToLayer(frameToBeSent)
        self._state = self.HAND1
        print ("CR enviado. Estado atual GER:", self._state)
        self.enable_timeout()
    
    def connConfirm(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CC)
        self.sendToLayer(frameToBeSent)
    
    def keepAliveRequest(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.KR)
        self._state = self.CHECK
        self.sendToLayer(frameToBeSent)
        self.changeTimeoutValue(self._initialTimeout)
        self.reload_timeout()
        self.enable_timeout()
    
    def keepAliveConfirm(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.KC)
        self.sendToLayer(frameToBeSent)

    def connAccepted(self):
        frameToBeSent = bytearray()
        frameToBeSent.append(self.gerID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CA)
        self.sendToLayer(frameToBeSent)   

    def setBottom(self, bottom):
        self._bottom = bottom

    def setTop(self, top):
        self._top = top

    def handle(self):
        if(self._state == self.CONN or self._state == self.CHECK or self._state == self.HALF1):    
            frame = sys.stdin.readline()
            frameToBeSent = bytearray()
            frameToBeSent.append(self.gerID)
            frameToBeSent.append(self.byteDATA)
            for i in range(len(frame) - 1):
                frameToBeSent.append(int.from_bytes(frame[i].encode('ascii'), 'big'))
            self.sendToLayer(frameToBeSent)

    def handle_timeout(self):
        if(self._state == self.HAND1):
            self.connRequest()
        elif(self._state == self.CONN):
            self.keepAliveRequest()
        elif(self._state == self.CHECK):
            self.keepAliveRequest()


    def sendToLayer(self, data):
        self._bottom.receiveFromTop(data)

    def notifyLayer(self, data):
        pass

    def receiveFromBottom(self, recvFromARQ):
       self.handle_fsm(recvFromARQ)

    def handle_fsm(self, recvFromARQ):
        if (self._state == self.DISC):
            if (recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                self.connConfirm()
                self._state = self.HAND2
                self.enable_timeout()

        elif (self._state == self.HAND1):
            if (recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                print("CR recebido. Enviando CC")
                self.connConfirm()
            elif (recvFromARQ[1] == self.CC and recvFromARQ[0] == self.byteGER):
                print ("CC recebido. Enviando CA e indo para CONN")
                self.connAccepted()
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()   
                self.enable_timeout()             
                print ("Conexão estabelecida")
            elif (recvFromARQ[1] == self.CA and recvFromARQ[0] == self.byteGER):
                print ("CA recebido. Indo para CONN")
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
                

        elif (self._state == self.CONN):
            if(recvFromARQ[1] == self.CR and recvFromARQ[0] == self.byteGER):
                self.connConfirm()
            elif(recvFromARQ[1] == self.KR and recvFromARQ[0] == self.byteGER):
                self.keepAliveConfirm()
                self.disable_timeout()
            elif(recvFromARQ[0] == self.byteDATA):
                print(recvFromARQ.decode('ascii'))
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable_timeout()
        
        elif(self._state == self.CHECK):
            if(recvFromARQ[1] == self.KR and recvFromARQ[0] == self.byteGER):
                self.keepAliveConfirm()
                print("enviando kc")
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable()
            elif(recvFromARQ[1] == self.KC and recvFromARQ[0] == self.byteGER):
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable()
            elif(recvFromARQ[0] == self.byteDATA):
                print(recvFromARQ.decode('ascii'))
                self._state = self.CONN
                self.changeTimeoutValue(self.checkInterval)
                self.reload_timeout()
                self.enable()        
        print("Estado atual GER:", self._state)
            
