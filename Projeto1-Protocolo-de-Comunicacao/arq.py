#!/usr/bin/python3


import serial, sys, enum
import poller
import crc

class ARQ(poller.Layer):
    def __init__(self, obj, timeout):
        self._top = sys.stdin
        self._bottom = None
        
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = obj

    def setBottom(self, bottom):
        self._bottom = bottom

    def handle(self):
        quadro = sys.stdin.readline()
        self.sendToLayer(quadro)
    
    def handle_timeout(self):
        print('Timeout ! Nenhum dados recebido do teclado por enquanto')
    
    def receiveFromBottom(self, dados):
        print("Recebido do enquadramento: ", dados.decode('ascii'))

    def sendToLayer(self, dados):
        self._bottom.send(dados)
    
    def notifyLayer(self, dados):
        print(dados)