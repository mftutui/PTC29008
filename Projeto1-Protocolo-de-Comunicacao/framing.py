#!/usr/bin/python3
# -*- coding: utf-8 -*- 

__author__ = "Paulo Sell e Maria Fernanda Tutui"

import layer
import crc

class Framing(layer.Layer):
    '''
    Classe responsável por enquadradar um quadro e transmitir via interface serial
    '''
    # Estados da máquina de estados desta classe
    idle = 1
    rx = 2
    esc = 3

    def __init__(self, dev, bytes_min, bytes_max, timeout):
        ''' dev: interface serial para receber/enviar dados.
            bytes_min: número mínimo de bytes do quadro.
            bytes_max: número máximo de bytes do quadro.
            timeout: intervalo de tempo para interrupção interna
        '''
        self._bytes_min = bytes_min
        self._bytes_max = bytes_max
        self._state = self.idle
        self._dev = dev
        self._datasize = 0
        self._received = bytearray()
        self.fd = dev
        self.timeout = timeout
        self.base_timeout = timeout
        self.disable_timeout()
        self._crc = crc.CRC16(" ")
        self._top = None
        self.enable()


    def handle(self):
        ''' Trata o evento de recebimento de bytes pela interface serial  
        '''
        byte = self._dev.read()        
        self.handle_fsm(byte)
        
    def handle_timeout(self):
        ''' Trata a interrupção interna devido ao timeout
        '''
        print('Timeout Framing!')
        self.handle_fsm(None)
        
    def receiveFromTop(self, data):
        ''' Envia o quadro de dados pela interface serial
            data: bytearray representando o quadro a ser enviado
        '''         
        self._crc.clear()
        self._crc.update(data)
        msg = self._crc.gen_crc()
        self._dev.write(b'~')    
        for i in range (len(msg)):
            if (bytes([msg[i]]) == b'~' or bytes([msg[i]]) == b'}'):
                self._dev.write(b'}')
                if (bytes([msg[i]]) == b'~'):
                    self._dev.write(b'^')
                elif (bytes([msg[i]]) == b'}'):
                    self._dev.write(b']')
            else:              
                self._dev.write(bytes([msg[i]]))        
        self._dev.write(b'~')
       

    def  handle_fsm(self, byte):
        ''' Recebe um byte e faz seu tratamento na máquina de estados
            byte: byte recebido pela interface serial
        '''
        if byte == None:
            self._state = self.idle
            self._idle(None)            
        elif self._state == self.idle:
            self._idle(byte)
        elif self._state == self.rx:
            self._rx(byte)
        elif self._state == self.esc:
            self._esc(byte)

    def _idle(self, byte):
        ''' Trata o byte quando a máquina de estados está no estado idle
            byte: byte recebido pela interface serial
        '''        
        if byte is None:
            self._received.clear()
            self._datasize = 0
            self.disable_timeout()            
        elif((byte == b'~') and (self._datasize == 0)):
            self._state = self.rx       
            self.enable_timeout()
        else:
            self._state = self.idle
            self.disable_timeout()

    def notifyLayer(self, data):
        ''' Envia o data recebido para a camada superior
            data: bytearray representando o data recebido
        '''
        self._top.receiveFromBottom(data)

    def _rx(self, byte):
        ''' Trata o byte quando a máquina de estados está no estado rx
            byte: byte recebido pela interface serial
        '''              
        if (self._datasize > self._bytes_max):
            self.disable_timeout()
            self._state = self.idle
            self._datasize = 0
            self._received.clear()
        elif(byte == b'~' and self._datasize >= self._bytes_min):            
            self._crc.clear()
            self._crc.update(self._received)
            if self._crc.check_crc():
                self.notifyLayer(self._received[:self._datasize-2])
            self.disable_timeout()
            self._state = self.idle          
            self._datasize = 0            
            self._received.clear()            
        elif(byte == b'}'):
            self._state = self.esc
        elif(byte == b'~' and self._datasize == 0):
            self._state = self.rx
        elif (byte != b'~' or byte != b'}'):            
            self._received.append(int.from_bytes(byte, 'big'))
            self._datasize = self._datasize+1

    def _esc(self, byte):
        ''' Trata o byte quando a máquina de estados está no estado rx
            byte: byte recebido pela interface serial
        '''
        if(byte == b'~' or byte == b'}'):
           self._received.clear()
           self._datasize = 0
           self._state = self.idle
           self.disable_timeout()
        elif(byte == b'^'):
           self._received.append(int.from_bytes(b'~', 'big'))
           self._datasize = self._datasize + 1
           self._state = self.rx
        elif(byte == b']'):
           self._received.append(int.from_bytes(b'}', 'big'))
           self._datasize = self._datasize + 1
           self._state = self.rx

