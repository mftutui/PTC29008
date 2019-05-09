import serial
import sys
import layer

if __name__ == '__main__':

    if(len(sys.argv) < 2):
        print()
        print("#############################################################")
        print()
        print("Uso: python3 protoPPP.py --serialPath /dev/XXX [--fakeLayer]")
        print()
        print("--fakeLayer: utiliza o terminal para enviar e receber dados")
        print()
        print("#############################################################")
        print()
        sys.exit(0)
    #dev = serial.Serial(sys.argv[1])
    serialPath = ""
    isTun = True
    for i in range (len(sys.argv)-1):
        if sys.argv[i] == "--serialPath":
           serialPath = sys.argv[i+1]
           if(serialPath[:5] != "/dev/"):
                print("Uso: python3 protoPPP.py --serialPath /dev/XXX")
                sys.exit(0)
    
    if len(serialPath) == 0:
        print("Uso: python3 protoPPP.py --serialPath /dev/XXX")
        sys.exit(0)

    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--fakeLayer":
            isTun = False
    
    proto = layer.Protocolo(serialPath,isTun)
    proto.start()