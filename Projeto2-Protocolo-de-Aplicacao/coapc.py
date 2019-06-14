import socket 
import poller
import response
import random

class coap(poller.Callback):
    version                 = 1
    CON                     = 0
    NON                     = 1
    ACK                     = 2
    tokenLength             = 1
    codeCONTENT             = 69
    codeGET                 = 1
    codePOST                = 2
    codeVALID               = 67
    codeCREATED             = 65
    codePUT                 = 3
    codeDELETE              = 4
    optionContenFormat      = 192  # (0xC0) 
    optionURIPATH           = 176  # (0xB0)
    end                     = 255  # (0xFF)
    idle                    = 0
    wait                    = 1
    wait2                   = 2

    

    def __init__(self, ip):
        self.p = poller.Poller()
        self.ip = ip
        self.coapRequest = bytearray()
        self.servidor = (ip,5683)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('::', 0))
        self.fd = self.sock
        self.enable()
        self.disable_timeout()
        self.base_timeout = 10
        self.timeout = 10
        self.state = coap.idle
        
        
    def handle_fsm(self, frame):
        if(self.state == coap.idle):
            self.sock.sendto(self.coapRequest, self.servidor)
            self.state = coap.wait
        elif (self.state == coap.wait):
            if(((frame[0] >> 4) == 6) and frame[1] == 0): 
                self.state = coap.wait2
            else:
                if ((frame[0] >> 4) != 4):
                    if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED or frame[1] == coap.codeVALID):
                        type = (frame[0] & 48) >> 4                        
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = frame[5+tkllen:]
                        self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                        self.disable()
                        
                        
                elif((frame[0] >> 4) == 4):
                    if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED or frame[1] == coap.codeVALID):                        
                        type = (frame[0] & 48) >> 4    
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = frame[5+tkllen:]
                        self.response = response.Response(type, tkllen, code, mid, token, payload) 
                        self.sendACK(frame[2], frame[3])                        
                        self.disable()     
                           
                            
        elif (self.state == coap.wait2):         
            if ((frame[0] >> 4) != 4):
                if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED or frame[1] == coap.codeVALID):
                    type = (frame[0] & 48) >> 4 
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = frame[5+tkllen:]
                    self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                    self.disable()
                    
                        
            elif((frame[0] >> 4) == 4):
                if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED or frame[1] == coap.codeVALID):                       
                    type = (frame[0] & 48) >> 4 
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = frame[5+tkllen:]
                    self.response = response.Response(type, tkllen, code, mid, token, payload) 
                    self.sendACK(frame[2], frame[3])                        
                    self.disable()     
                      

    def sendACK(self, id1, id2):
        toBeSent = bytearray()
        toBeSent.append(0x60)
        toBeSent.append(0x00)
        toBeSent.append(id1)
        toBeSent.append(id2)
        self.sock.sendto(toBeSent,self.servidor)
    
    def handle(self):
        self.handle_fsm(self.sock.recv(4096))
        

    def handle_timeout(self):
        pass
    
    def do_get(self, type, *uris):            
            firstByteID = random.randint(0,255)
            secondByteID = random.randint(0,255)
            token = random.randint(0,255)
            firstByteofFrame = (coap.version << 6) | (type << 4) | (coap.tokenLength << 0)
            self.coapRequest.append(firstByteofFrame)
            self.coapRequest.append(coap.codeGET)
            self.coapRequest.append(firstByteID)
            self.coapRequest.append(secondByteID)
            self.coapRequest.append(token)
            for i in range (len(uris)):
                if (i == 0):
                    self.coapRequest.append((coap.optionURIPATH) | (len(uris[i]) << 0))
                else:
                    self.coapRequest.append(0 | (len(uris[i]) << 0))
                for j in range (len(uris[i])):
                    self.coapRequest.append(ord(uris[i][j]))      
            self.coapRequest.append(coap.end)
            print(self.coapRequest)        
            self.handle_fsm(self.coapRequest) 
            self.p.adiciona(self)
            self.p.despache()    
            return self.response

            
        

    def do_post(self, type, payload = None, *uris):
            firstByteID = random.randint(0,255)
            secondByteID = random.randint(0,255)
            token = random.randint(0,255)
            firstByteofFrame = (coap.version << 6) | (type << 4) | (coap.tokenLength << 0)
            self.coapRequest.append(firstByteofFrame)
            self.coapRequest.append(coap.codePOST)
            self.coapRequest.append(firstByteID)
            self.coapRequest.append(secondByteID)
            self.coapRequest.append(token)
            
            for i in range (len(uris)):
                if (i == 0):
                    self.coapRequest.append((coap.optionURIPATH) | (len(uris[i]) << 0))
                else:
                    self.coapRequest.append(0 | (len(uris[i]) << 0))
                for j in range (len(uris[i])):
                    self.coapRequest.append(ord(uris[i][j]))  
            self.coapRequest.append(0x11)
            self.coapRequest.append(0x2a)    
            self.coapRequest.append(coap.end)

            for i in range (len(payload)):
                self.coapRequest.append(payload[i])
            #self.coapRequest.append(0x10)
            print(self.coapRequest)        
            self.handle_fsm(self.coapRequest) 
            self.p.adiciona(self)
            self.p.despache()    
            return self.response

  
    
    def do_put(self, url, payload=None):
        pass
    
    def do_delete(self, url, payload=None):
        pass