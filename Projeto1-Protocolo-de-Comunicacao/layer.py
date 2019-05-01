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

class Protocolo():
  def __init__(self, serial):
    import arq
    import framing
    import gerencia
    self._poller = poller.Poller()
    self._arq = arq.ARQ(5)
    self._ger = gerencia.GER(sys.stdin, 9)
    self._enq = framing.Framing(serial, 1, 1024, 3)

  def start(self):
    print ("Estabelecendo conexão...")
    self._enq.setTop(self._arq)
    self._arq.setBottom(self._enq)
    self._arq.setTop(self._ger)
    self._ger.setBottom(self._arq)
    self._ger.connRequest()
    self._poller.adiciona(self._enq)
    self._poller.adiciona(self._arq)
    self._poller.adiciona(self._ger)
    self._poller.despache()
