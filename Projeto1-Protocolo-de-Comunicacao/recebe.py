import serial, sys, enum
from framing import Framing

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/5')

    enq = Framing(dev, 1, 1024)

    while True:
        enq.handle()
        print (enq.getRecebido())
