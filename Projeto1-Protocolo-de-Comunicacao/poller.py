#!/usr/bin/python3

import selectors
import time
import sys

    
class Callback:
  def __init__(self, fileobj=None, timeout=0):
      '''Cria um objeto Callback. 
      fileobj: objeto tipo arquivo, podendo ser inclusive 
      um descritor de arquivo numérico.
      timeout: valor de timeout em segundos, podendo ter parte 
      decimal para expressar fração de segundo'''
      if timeout < 0: raise ValueError('timeout negativo')
      self.fd = fileobj
      self.timeout = timeout
      self._enabled_to = True
      self.base_timeout = timeout

  def handle(self):
      '''Trata o evento associado a este callback. Tipicamente 
      deve-se ler o fileobj e processar os dados lidos. Classes
      derivadas devem sobrescrever este método.'''
      pass

  def handle_timeout(self):
      '''Trata um timeout associado a este callback. Classes
      derivadas devem sobrescrever este método.'''
      pass

  def update(self, dt):
      'Atualiza o tempo restante de timeout'
      self.timeout = max(0, self.timeout - dt)

  def reload_timeout(self):
      'Recarrega o valor de timeout'
      self.timeout = self.base_timeout

  def disable_timeout(self):
      'Desativa o timeout'
      self._enabled_to = False

  def enable_timeout(self):
      'Reativa o timeout'
      self._enabled_to = True

  @property
  def timeout_enabled(self):
      return self._enabled_to
  
  @property
  def isTimer(self):
      'true se este callback for um timer'
      return self.fd == None



class Layer(Callback):
 
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

class Poller:
  def __init__(self):
    self.cbs_to = []
    self.sched = selectors.DefaultSelector()

  def adiciona(self, cb):
    'Registra um callback'
    if cb.isTimer and not cb in self.cbs_to: self.cbs_to.append(cb)
    else:
      self.sched.register(cb.fd, selectors.EVENT_READ, cb)

  def _compareTimeout(self, cb, cb_to):
    if not cb.timeout_enabled: return cb_to
    if not cb_to:
        cb_to = cb
    elif cb_to.timeout > cb.timeout:
      cb_to = cb
    return cb_to

  def _timeout(self):
    cb_to = None
    for cb in self.cbs_to: cb_to = self._compareTimeout(cb, cb_to)
    for fd,key in self.sched.get_map().items():
      cb_to = self._compareTimeout(key.data, cb_to)
    return cb_to

  def despache(self):
    '''Espera por eventos indefinidamente, tratando-os com seus
    callbacks'''
    while True: self.despache_simples()

  def despache_simples(self):
    'Espera por um único evento, tratando-o com seu callback'
    t1 = time.time()
    cb_to = self._timeout()
    if cb_to != None:
        tout = cb_to.timeout
    else:
        tout = None
    eventos = self.sched.select(tout)
    if not eventos: # timeout !
      if cb_to != None:
          cb_to.handle_timeout()
          #cb_to.reload_timeout()

    else:
      for key,mask in eventos:
        cb = key.data # este é o callback !
        cb.handle()
        cb.reload_timeout()
    dt = time.time() - t1
    for cb in self.cbs_to: 
      if cb != cb_to: cb.update(dt)
    for fd,key in self.sched.get_map().items():
        cb = key.data
        if cb != cb_to: cb.update(dt)


class Protocolo():
  def __init__(self, serial):
    import arq
    import framing
    self._poller = Poller()
    self._arq = arq.ARQ(sys.stdin,5)
    self._enq = framing.Framing(serial, 1, 1024, 3)

  def start(self):
    print ("Sistema iniciado! Digite uma mensagem para ser enviada:")
    self._enq.setTop(self._arq)
    self._arq.setBottom(self._enq)
    self._poller.adiciona(self._enq)
    self._poller.adiciona(self._arq)
    self._poller.despache()

            
            
