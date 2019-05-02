import serial
import layer

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/5')
    proto = layer.Protocolo(dev)
    proto.start()



