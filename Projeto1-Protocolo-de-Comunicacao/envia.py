import serial, sys, enum
from framing import Framing
from arq import ARQ
import string, random
import poller
import sys,time

if __name__ == '__main__':
     
    dev = serial.Serial('/dev/pts/4')
    
    enq = Framing(dev, 1, 1024, 1)
    arq = ARQ(sys.stdin, 10)
    enq.setTop(arq)
    arq.setBottom(enq)
    sched = poller.Poller()
    proto = poller.Protocolo(sched)
    proto._poller.adiciona(enq)
    proto._poller.adiciona(arq)
    proto.start()
    
 
    
       

