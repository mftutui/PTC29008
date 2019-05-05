import poller
import sys
import signal

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

class FakeLayer(Layer):
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

  def receiveFromBottom(self, data):
    print(data.decode('ascii'))

  def handle(self):
    frame = sys.stdin.readline()
    frameToBeSent = bytearray()
    for i in range(len(frame) - 1):
      frameToBeSent.append(int.from_bytes(frame[i].encode('ascii'), 'big'))
    self.sendToLayer(frameToBeSent)


  def sendToLayer(self, data):
    self._bottom.receiveFromTop(data)
  
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
    self._arq = arq.ARQ(None, 1)
    self._ger = gerencia.GER(None,55,9)
    self._enq = framing.Framing(serial, 1, 1024, 3)
    self._fake = FakeLayer(sys.stdin, 10)


  def start(self):
    try:
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
    except KeyboardInterrupt:
      print("enviando DR")
      self._ger.disconRequest() 
      self._ger._state = self._ger.HALF1
  
  
    