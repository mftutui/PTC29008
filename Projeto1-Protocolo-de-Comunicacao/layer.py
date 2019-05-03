import poller
import sys


class Layer(poller.Callback):
 
  def __init__(self, top=None, bottom=None):
    self._top = top
    self._bottom = bottom

  def handle(self):
    pass
  def handle_timeout(self):
    pass

  def sendToLayer(self, data):
    pass

  def notifyLayer(self, data):
    pass

class fakeLayer(Layer):
  def __init__(self, fd, timeout):
        self._top = None
        self._bottom = None
        self.timeout = timeout
        self.fd = sys.stdin
        self.base_timeout = timeout
        self.disable_timeout()
        self.enable()

  def handle_timeout(self):
        pass

  def handle(self):
        a = sys.stdin.readline()
        print("lido", a)
        self.sendToLayer(a)

  def sendToLayer(self, data):
        self._bottom.send(data)
  
  def notifyLayer(self, data):
        pass
  
  def setTop(self, top):
        self._top = top

  def setBottom(self, bottom):
        self._bottom = bottom

class Protocolo():
  def __init__(self, serial):
    import arq
    import framing
    import gerencia
    self._poller = poller.Poller()
    self._arq = arq.ARQ(None, 5)
    self._ger = gerencia.GER(None, 9)
    self._enq = framing.Framing(serial, 1, 1024, 3)
    self._fake = fakeLayer(sys.stdin, 10)

  def start(self):
    print ("Estabelecendo conexão...")
    self._enq.setTop(self._arq)
    self._arq.setBottom(self._enq)
    self._arq.setTop(self._ger)
    self._ger.setBottom(self._arq)
    self._ger.setTop(self._fake)
    self._fake.setBottom(self._ger)
    self._ger.connRequest()
    self._poller.adiciona(self._enq)
    self._poller.adiciona(self._arq)
    self._poller.adiciona(self._ger)
    self._poller.adiciona(self._fake)
    self._poller.despache()
