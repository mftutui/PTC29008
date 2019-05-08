#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import layer
import sys
import time
import tun

class TunLayer(layer.Layer):
    def __init__(self, tun, timeout):
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = tun.fd
        self._tun = tun
        self._top = None
        self._bottom = None
        self.disable_timeout()
        self.enable()

    def setTop(self, top):
        self._top = top
    
    def setBottom(self, bottom):
        self._bottom = bottom

    def handle(self):
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
        print("Timeout!")
    
    def sendToLayer(self, data):
        self._bottom.receiveFromTop(data)

    def notifyLayer(self, data):
        pass

    def receiveFromBottom(self, data):
       lenProto = data[0]
       proto = int(data[1:lenProto+1].decode('ascii'), 16) 
       payload = data[lenProto+1:]
       self._tun.send_frame(payload, proto)
