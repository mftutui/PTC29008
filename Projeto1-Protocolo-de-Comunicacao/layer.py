#!/usr/bin/python3
# -*- coding: utf-8 -*- 

''' 
Layer e Protocolo
'''

import poller
import sys
from tun import Tun

class Layer(poller.Callback):
    ''' 
    Classe abstrata herdeira de poller.Calback para acrescentar
    camadas ao protocolo
    '''
    def __init__(self):
      self._top = None
      self._bottom = None

    def handle(self):
      '''Trata o evento associado a este callback. Tipicamente 
      deve-se ler o fileobj e processar os dados lidos. Classes
      derivadas devem sobrescrever este método.'''
      pass
    def handle_timeout(self):
      ''' Trata a interrupção interna devido ao timeout
      ''' 
      pass

    def sendToLayer(self, data):
      ''' Envia o frame a ser transmitido para a camada inferior
          data: bytearray representando o frame a ser transmitido
      '''  
      pass

    def notifyLayer(self, data):
      ''' Envia o frame recebido para a camada superior
          data: bytearray representando o frame a ser enviado
      '''
      pass

class FakeLayer(Layer):
    '''
      Classe para receber dados do teclado e transmiti-los
    '''
    def __init__(self, fd, timeout):
      ''' fd: descritor de arquivos sys.stdin
          timeout: timeout: intervalo de tempo para interrupção interna
      '''
      self._top = None
      self._bottom = None
      self.timeout = timeout
      self.fd = sys.stdin
      self.base_timeout = timeout
      self.disable_timeout()
      self.enable()

    def handle_timeout(self):
      ''' Trata a interrupção interna devido ao timeout
      ''' 
      pass

    def receiveFromBottom(self, data):
      ''' Recebe um quadro da camada inferior
          data: bytearray representando o quadro recebido
      ''' 
      print(data.decode('ascii'))

    def handle(self):
      ''' Trata o evento de recebimento de bytes pela interface serial  
      '''
      frame = sys.stdin.readline()
      frameToBeSent = bytearray()
      for i in range(len(frame) - 1):
        frameToBeSent.append(int.from_bytes(frame[i].encode('ascii'), 'big'))
      self.sendToLayer(frameToBeSent)

    def sendToLayer(self, data):
      ''' Envia o frame a ser transmitido para a camada inferior
          data: bytearray representando o frame a ser transmitido
      '''  
      self._bottom.receiveFromTop(data)
    
    def notifyLayer(self, data):
      ''' Envia o frame recebido para a camada superior
          data: bytearray representando o frame a ser enviado
      ''' 
      pass
    
    def setTop(self, top):
      ''' Método para definir camada superior da classe arq
          top: objeto da camada superior
      '''
      self._top = top

    def setBottom(self, bottom):
      ''' Método para definir camada inferior da classe arq
          bottom: objeto da camada inferior
      '''
      self._bottom = bottom

class Protocolo():
    '''
    Classes para inicializar as camadas do protocolo
    '''
    def __init__(self, serial, isTun):
      ''' serial: interface serial para troca de dados
      '''
      import arq
      import framing
      import gerencia
      import tunlayer
      import serial

      self._dev = serial.Serial()
      self._isTun = isTun

      if (self._isTun == True):
        self._tun = Tun("tun0", "10.0.0.1", "10.0.0.2", mask="255.255.255.252", mtu=1500, qlen=4)
        self._tun.start()      
        self._tunLayer = tunlayer.TunLayer(self._tun, 10)
      else:
        self._fake = FakeLayer(sys.stdin, 10)

      self._poller = poller.Poller()
      self._arq = arq.ARQ(None, 1)
      self._ger = gerencia.GER(None,254,10)
      self._enq = framing.Framing(serial, 1, 1024, 3)

    def start(self):
      ''' Configura as ligações das camadas e despacha os callbacks
      '''
      try:
        print ("Estabelecendo conexão...")
        if (self._isTun == True):
          self._tunLayer.setBottom(self._ger)
          self._ger.setTop(self._tunLayer)
          self._poller.adiciona(self._tunLayer)
        else: 
          self._fake.setBottom(self._ger)
          self._ger.setTop(self._fake)
          self._poller.adiciona(self._fake)

        self._enq.setTop(self._arq)
        self._arq.setBottom(self._enq)
        self._arq.setTop(self._ger)
        self._ger.setBottom(self._arq)
        self._ger.connRequest()
        self._poller.adiciona(self._enq)
        self._poller.adiciona(self._arq)
        self._poller.adiciona(self._ger)
        
        self._poller.despache()
      except KeyboardInterrupt:
        print("enviando DR e encerrando a sessão")
        self._ger.disconRequest() 
        self._ger._state = self._ger.HALF1