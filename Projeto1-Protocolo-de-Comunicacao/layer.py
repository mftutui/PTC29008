#!/usr/bin/python3
# -*- coding: utf-8 -*- 

''' 
Layer
'''

import poller



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

    def receiveFromBottom(self, data):
      pass

    
    def receiveFromTop(self, data):
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



    