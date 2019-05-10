#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Layer e Protocolo
'''

import poller
import sys
import tun
import time
import os
import fakelayer
import arq
import framing
import gerencia
import tunlayer
import serial


class PPP():
    '''
    Classes para inicializar as camadas do protocolo
    '''

    def __init__(self, serialPath, isTun, id):
        ''' serial: interface serial para troca de dados
        '''
        self._isTun = isTun
        if (self._isTun == True):
            try:
                self._dev = serial.Serial(serialPath)
            except:
                print("Verifique se a porta serial foi criada")
                print()
                sys.exit(0)

            try:
                self._tun = tun.Tun("tun0", "10.0.0.1", "10.0.0.2", mask="255.255.255.252", mtu=1500, qlen=4)
                self._tun.start()
            except Exception:
                print("Você deve executar o programa como root!!!")
                print()
                sys.exit(0)
            self._poller = poller.Poller()
            self._arq = arq.ARQ(None, 1)
            self._ger = gerencia.GER(None, id, 10)
            self._enq = framing.Framing(self._dev, 1, 1024, 3)
            self._tunLayer = tunlayer.TunLayer(self._tun, 10)

            # self._fake = FakeLayer(sys.stdin, 10)
        else:
            try:
                self._dev = serial.Serial(serialPath)
            except:
                print("Verifique se a porta serial foi criada")
                print()
                sys.exit(0)
            self._poller = poller.Poller()
            self._arq = arq.ARQ(None, 1)
            self._ger = gerencia.GER(None, id, 10)
            self._enq = framing.Framing(self._dev, 1, 1024, 3)
            # self._tunLayer = tunlayer.TunLayer(self._tun, 10)
            self._fake = fakelayer.FakeLayer(sys.stdin, 10)

    def loadingBar(self, times):
        buffer = []
        repeat = 0

        while repeat < times:
            for i in range(repeat):
                buffer.append('%')
            os.system('clear')
            buf = ''.join(buffer)
            print(buf)
            time.sleep(0.2)
            repeat = repeat + 1;

    def start(self):
        ''' Configura as ligações das camadas e despacha os callbacks
        '''
        try:
            if (self._isTun == True):
                print ("Estabelecendo conexão...")
                self._enq.setTop(self._arq)
                self._arq.setBottom(self._enq)
                self._arq.setTop(self._ger)
                self._ger.setBottom(self._arq)
                self._ger.setTop(self._tunLayer)
                self._tunLayer.setBottom(self._ger)
                self._ger.connRequest()
                self._poller.adiciona(self._enq)
                self._poller.adiciona(self._arq)
                self._poller.adiciona(self._ger)
                self._poller.adiciona(self._tunLayer)
                self._poller.despache()
            else:
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
            os.system('clear')
            self._ger.disconRequest()
            self._ger._state = self._ger.HALF1
            self.loadingBar(13)

            os.system('clear')
            print('Desconectado')
            print()
            sys.exit(0)