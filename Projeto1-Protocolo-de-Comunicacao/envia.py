import serial, sys, enum
from framing import Transmission


if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/7')
    
    bytes = [b'~', b'a', b'b', b'c', b'd', b'~']
    enq = Transmission(dev)

    for byte in bytes[:]:
        print (byte)
        enq.handle(byte)
        bytes.remove(byte)
    
    print (len(bytes))   
