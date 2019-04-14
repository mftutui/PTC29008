import serial
import poller


if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/6')
    proto = poller.Protocolo(dev)
    proto.start()
    
