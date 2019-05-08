import serial
import layer

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/2')
    proto = layer.Protocolo(dev)
    proto.start()
