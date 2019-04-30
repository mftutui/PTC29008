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
    byteID = 0xFE
    CR = 0x00
    CC = 0x01
    CA = 0x07
    DR = 0x04

    def __init__(self, fd, timeout):
        self.fd = fd
        self.timeout = timeout
        self.base_timeout = timeout
        self._top = None
        self._bottom = None
        self.enable()
        self.disable_timeout()

    def setBottom(self, bottom):
        self._bottom = bottom

    def setTop(self, top):
        self._top = top

    def handle(self):
        frame = sys.stdin.readline()
        frameToBeSent = bytearray()
        frameToBeSent.append(self.byteID)
        for i in range(len(frame) - 1):
            frameToBeSent.append(int.from_bytes(frame[i].encode('ascii'), 'big'))
        self.sendToLayer(frameToBeSent)

    def handle_timeout(self):
        print ("timeout ger")

    def sendToLayer(self, data):
        self._bottom.receiveFromTop(data)

    def notifyLayer(self, data):
        pass

    def receiveFromBottom(self, recvFromARQ):
       self.handle_fsm(recvFromARQ)

    def handle_fsm(self, recvFromARQ):
        print(recvFromARQ.decode('ascii'))
