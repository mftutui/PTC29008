import serial
import layer
import sys

if __name__ == '__main__':
    serialPath = ''
    isTun = True

    for i in range (len(sys.argv)-1):
        if sys.argv[i] == "--serialPath":
            serialPath = sys.argv[i+1]
            if (serialPath.find("/dev/") == -1):
                print("Uso: python3 envia.py --serialPath /dev/XXX")
                sys.exit(0)

    if (len(serialPath) == 0):
        print("Uso: python3 envia.py --serialPath /dev/XXX")
        sys.exit(0)

    for i in range (len(sys.argv)):
        if sys.argv[i] == "--fakeLayer":
            isTun = False

    proto = layer.Protocolo(serialPath, isTun)
    proto.start()