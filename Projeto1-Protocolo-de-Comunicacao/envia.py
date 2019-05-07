import serial
import layer

if __name__ == '__main__':

    dev = serial.Serial('/dev/pts/3')
    proto = layer.Protocolo(dev)




