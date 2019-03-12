import serial, sys, enum
from framing import Framing
import string, random

if __name__ == '__main__':
    dev = serial.Serial('/dev/pts/3')
    
    framesize = random.randint(1,15)
    quadro = ""
    i = 0
    print (framesize)
    while i < framesize:
        aux = random.randint(1,3)
        if aux == 1:
            a = random.choice(string.ascii_letters)
            quadro = quadro + a
            i = i + 1
        elif aux == 2:
            a = random.choice(string.digits)
            quadro = quadro + a
            i = i + 1
        elif aux == 3:
            a = random.choice(string.punctuation)
            quadro = quadro + a
            i = i + 1
        
    enq = Framing(dev, 1, 1024, 3)
    print (quadro)
    enq.send(str(quadro), len(quadro))
    
 
    
       
