import poller
import sys

class GER(poller.Layer):
    DISC = 0
    HAND1 = 1
    HAND2 = 2
    CON = 3
    CHECK = 4
    HALF1 = 5
    HALF2 = 6

    def __init__(self, timeout):
        self.fd = sys.stdin
        self.timeout = timeout
        self.base_timeout = timeout
        self.disable_timeout()
        self._state = self.DISC
        self._top = None
        self._bottom = None
        
    def setTop(self, top):
        self._top = top
    
    def setBottom(self, bottom):
        self._bottom = bottom
    

    def handle(self):
        frame = sys.stdin.readline()
        self.sendToLayer(frame)
    
    def handle_timeout(self):
        print ("timeout")

    def notifyLayer(self, data):
        pass

    def sendToLayer(self, data):
        self._bottom.receiveFromTop(data)
    
    def receiveFromBottom(self, data):
        print(data)