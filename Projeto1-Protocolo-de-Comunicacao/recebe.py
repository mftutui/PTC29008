import serial, sys, enum
from framing import Framing
import poller
import sys,time

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/4')

    enq = Framing(dev, 1, 1024, 1)
    sched = poller.Poller()
    proto = poller.Protocolo(sched)
    proto._poller.adiciona(enq)
    proto.start()
    
