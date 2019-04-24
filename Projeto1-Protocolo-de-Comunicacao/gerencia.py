import poller
import sys

class GER(poller.Layer):
    DISC = 0
    HAND1 = 1
    HAND2 = 2
    CONN = 3
    CHECK = 4
    HALF1 = 5
    HALF2 = 6
    byteGER = 0xFF
    byteDATA = 0x00
    byteID = 0xFE
    CR = 0x00
    CC = 0x01
    CA = 0x07
    DR = 0x04


    def __init__(self, timeout):
        self.fd = sys.stdin
        self.timeout = timeout
        self.base_timeout = timeout
        self.disable_timeout()
        self._state = self.DISC
        self._top = None
        self._bottom = None
        self._is_connected = False
       
        

    def connRequest(self):
        if(self._is_connected == False):
            print("Enviando CR...")
            frameToBeSent = bytearray()
            frameToBeSent.append(self.byteID)
            frameToBeSent.append(self.byteGER)
            frameToBeSent.append(self.CR)
            self._state = self.HAND1
            self.sendToLayer(frameToBeSent)

    def connConfirm(self):
        print("Enviando CC...")
        frameToBeSent = bytearray()
        frameToBeSent.append(self.byteID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CC)        
        self.sendToLayer(frameToBeSent)
    
    def connAccepted(self):
        print("Enviando CA...")
        frameToBeSent = bytearray()
        frameToBeSent.append(self.byteID)
        frameToBeSent.append(self.byteGER)
        frameToBeSent.append(self.CA)
        self._state = self.CONN
        self.sendToLayer(frameToBeSent)

    def setTop(self, top):
        self._top = top
    
    def setBottom(self, bottom):
        self._bottom = bottom
    

    def handle(self):
        # if self._state == self.CONN:
            frame = sys.stdin.readline()
            frameToBeSent = bytearray()
            frameToBeSent.append(self.byteID)
            for i in range (len(frame)-1):
                frameToBeSent.append(int.from_bytes(frame[i].encode('ascii'),'big'))
            self.sendToLayer(frameToBeSent)
    
    def handle_timeout(self):
        print ("timeout")

    def notifyLayer(self, data):
        pass

    def sendToLayer(self, data):
        self._bottom.receiveFromTop(data)
    
    def receiveFromBottom(self, recvFromARQ):
       self.handle_fsm_ger(recvFromARQ)
    
    def handle_fsm_ger(self, recvFromARQ):
        print(recvFromARQ.decode('ascii'))        
        # if (self._state == self.DISC):
        #     if(recvFromARQ[1] == self.CR and recvFromARQ[0]==self.byteGER):
        #         self.connConfirm()
        #         self._state = self.HAND2
        
        # elif (self._state == self.HAND1):
        #     if(recvFromARQ[1] == self.CR and recvFromARQ[0]==self.byteGER):
        #         print("CR recebido")
        #         self.connConfirm()
        #         self._state == self.HAND1
        #         # print ("GER estava em HAND1, recebeu CR enviou CC e continuou em HAND1")
        #     elif(recvFromARQ[1] == self.CC and recvFromARQ[0]==self.byteGER):
        #         print("CC recebido")
        #         self.connAccepted()
        #         self._state = self.CONN
        #         # print ("GER estava em HAND1, recebeu CC enviou CA e foi para CONN")
        #     elif(recvFromARQ[1] == self.CA and recvFromARQ[0]==self.byteGER):
        #         print ("CA recebido")                
        #         self._state = self.CONN
        #         # print ("GER estava em HAND1, recebeu CA  foi para CONN")
        #         self._is_connected = True   

        # elif (self._state == self.HAND2):
        #     if(recvFromARQ[1] == self.CA or recvFromARQ[1] != self.DR or recvFromARQ[0]==self.byteDATA):
        #         self._state == self.CONN
        #         self._is_connected = True
        
        # elif (self._state == self.CONN):
        #     print(recvFromARQ[1:].decode('ascii'))   
        # print("Estado atual GER:", self._state)