#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Paulo Sell e Maria Fernanda Tutui"

import layer
import tun

class TunLayer(layer.Layer):

    '''
        Classe que faz a ligação entre a camada de gerencia e a interface Tun
    '''

    def __init__(self, tunobj):
        '''
            tunobj: objeto da classe Tun
        '''
        self.timeout = 10
        self.base_timeout = 10
        self.fd = tunobj.fd
        self._tun = tunobj
        self._top = None
        self._bottom = None
        self.disable_timeout()
        self.enable()


    def handle(self):
        ''' Trata o evento de recebimento de bytes pela interface Tun
        '''
        frame = self._tun.get_frame()
        proto = frame[0]
        payload = frame[1]
        protoHex = hex(proto)
        frameToBeSent = bytearray()
        frameToBeSent.append(len(protoHex))
        for i in range (len(protoHex)):
            frameToBeSent.append(int.from_bytes(protoHex[i].encode('ascii'),'big'))
        for i in range(len(payload)):
            frameToBeSent.append(payload[i])
        self.sendToLayer(frameToBeSent)
       
    
    def handle_timeout(self):
        ''' Trata a interrupção interna devido ao timeout
        '''
        pass
    
    def sendToLayer(self, data):
        ''' Envia o frame a ser transmitido para a camada inferior
          data: bytearray representando o frame a ser transmitido
        ''' 
        self._bottom.receiveFromTop(data)

    def notifyLayer(self, data):
        ''' Envia o frame recebido para a camada superior
          data: bytearray representando o frame a ser enviado
        '''
        lenProto = data[0]
        proto = int(data[1:lenProto + 1].decode('ascii'), 16)
        payload = data[lenProto + 1:]
        self._tun.send_frame(payload, proto)

    def receiveFromBottom(self, data):
        ''' Recebe um quadro da camada inferior
            data: bytearray representando o quadro recebido
        ''' 
        self.notifyLayer(data)

