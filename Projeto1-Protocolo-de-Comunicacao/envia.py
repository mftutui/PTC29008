import serial
import poller

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/2')
    proto = poller.Protocolo(dev)
    proto.start()



