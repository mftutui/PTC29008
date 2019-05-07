import serial
import layer

if __name__ == '__main__':
    dev = serial.Serial('/dev/ttys007')
    proto = layer.Protocolo(dev)
    proto.start()