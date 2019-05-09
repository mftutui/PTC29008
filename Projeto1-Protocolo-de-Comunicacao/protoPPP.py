import serial
import sys
import layer
import os

if __name__ == '__main__':
    os.system('clear')

    if(len(sys.argv) < 2) or (len(sys.argv) == 2 and sys.argv[1] == "-h")   :
        print()
        print("###################################################################")
        print()
        print("Uso: python3 protoPPP.py --serialPath /dev/XXX [opções] | -h")
        print()
        print("-h: Mostra este menu")
        print()
        print("--fakeLayer: utiliza o terminal para enviar e receber dados")
        print()
        print("--idSessao: informa a identificação da sessão a ser estabelecida")
        print()
        print("###################################################################")
        print()
        sys.exit(0)
    #dev = serial.Serial(sys.argv[1])
    serialPath = ""
    isTun = True
    id = 254


    for i in range (len(sys.argv)-1):
        if sys.argv[i] == "--idSessao":
            try:
                id = int(sys.argv[i + 1])
                if(id < 0 or id > 255):
                    print("Você deve inserir um valor entre 0 e 255 na identificação da sessão");
                    print()
                    sys.exit(0)

            except:
                print("Você deve inserir um valor entre 0 e 255 na identificação da sessão")
                print()
                sys.exit(0)



    for i in range (len(sys.argv)-1):
        if sys.argv[i] == "--serialPath":
           serialPath = sys.argv[i+1]
           if(serialPath[:5] != "/dev/"):
                print("Uso: python3 protoPPP.py --serialPath /dev/XXX")
                print()
                sys.exit(0)
    
    if len(serialPath) == 0:
        print("Uso: python3 protoPPP.py --serialPath /dev/XXX")
        print()
        sys.exit(0)

    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--fakeLayer":
            isTun = False
    
    proto = layer.Protocolo(serialPath,isTun, id)
    proto.start()