import serial, sys, enum
from framing import Framing
import poller
import sys,time

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/2')

    enq = Framing(dev, 1, 1024, 3)
    sched = poller.Poller()

    sched.adiciona(enq)


    sched.despache()
    
