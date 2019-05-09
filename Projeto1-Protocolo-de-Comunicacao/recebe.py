import serial
import sys
import layer

if __name__ == '__main__':
    
    #dev = serial.Serial(sys.argv[1])
    proto = layer.Protocolo(sys.argv[1], sys.argv[2])
    proto.start()
