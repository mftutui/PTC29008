import serial, sys, enum
from framing import Reception

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/8')

    enq = Reception(dev)

    while True:
        enq.handle()
        print (enq.getRecebido())
