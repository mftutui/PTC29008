#!/usr/bin/python3

from tun import Tun
import os
import time

tun = Tun("tun0","10.0.0.1","10.0.0.2",mask="255.255.255.252",mtu=1500,qlen=4)

tun.start()

while True:
  proto,payload = tun.get_frame()
  print("recebeu: proto=%s, payload=" % hex(proto), payload) 
  # aqui envio de volta pra tun o pacote recebido ...
  # você pode ver o pacote duplicado com o wireshark
  tun.send_frame(payload, proto)
