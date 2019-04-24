import serial
import poller


if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/18')
    proto = poller.Protocolo(dev)
    proto.start()
    
