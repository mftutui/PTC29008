#!/usr/bin/python3
# -*- coding: utf-8 -*- 
__author__ = "Paulo Sell e Maria Fernanda Tutui"
import socket 
import poller
import response
import random


class coap(poller.Callback):
    '''
        Classe que implementa o lado cliente do protoco CoAP. A classe é capaz de fazer requisições
        do tipo GET e POST.
    '''
    ACK_TIMEOUT              = 2
    ACK_RANDOM_FACTOR        = 1.5
    MAX_RETRANSMIT           = 4
    version                  = 1
    CON                      = 0
    NON                      = 1
    ACK                      = 2
    tokenLength              = 1
    codeEMPTY                = 0
    codeVALID                = 67
    codeINTERTALERROR        = 160
    codeCONTENT              = 69
    codeCREATED              = 65
    codeGET                  = 1
    codePOST                 = 2
    codePUT                  = 3
    codeDELETE               = 4
    octet_stream             = 42
    optionURIPATH            = 176  # (0xB0)
    end                      = 255  # (0xFF)
    idle                     = 0
    wait                     = 1
    wait2                    = 2
    

    def __init__(self, ip):
        '''
            O construtor da classe recebe como parâmetro o ip do servidor (IPv6)
        '''
        self.retransmitions = 0
        self.p = poller.Poller()
        self.ip = ip
        self.coapRequest = bytearray()
        self.servidor = (ip,5683)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(('::', 0))
        self.fd = self.sock
        self.enable()
        self.disable_timeout()
        self.base_timeout = random.uniform(coap.ACK_TIMEOUT,coap.ACK_TIMEOUT*coap.ACK_RANDOM_FACTOR)
        self.timeout = random.uniform(coap.ACK_TIMEOUT,coap.ACK_TIMEOUT*coap.ACK_RANDOM_FACTOR)
        self.state = coap.idle
        
    
    def _changeTimeoutValue(self, timeout):
        ''' Altera o valor do timeout do objeto
            timeout: novo valor do timeout
        '''
        self.base_timeout = timeout

    def _reloadAndEnableTimeout(self):
        ''' Altera o valor do timeout do objeto
        '''
        self.reload_timeout()
        self.enable_timeout()

    def handle_fsm(self, frame):
        '''
            Método que implementa a máquina de estados do cliente CoAP. Recebe como parametro
            um bytearray com o quadro a ser transmitido para o servidor ou o quadro recebido 
            do servidor
        '''
        if(self.state == coap.idle):
            self.sock.sendto(self.coapRequest, self.servidor)
            self.state = coap.wait
            self.enable_timeout()
        elif (self.state == coap.wait):
            if(((frame[0] >> 4) == 6) and frame[1] == 0): 
                self.state = coap.wait2
                self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                self.reload_timeout()                 
                self.retransmitions = 0                
            else:
                if ((frame[0] >> 4) != 4):
                    if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED 
                    or frame[1] == coap.codeVALID):
                        type = (frame[0] & 48) >> 4                        
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = frame[5+tkllen:]
                        self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                        self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                        self.reload_timeout()
                        self.disable_timeout() 
                        self.retransmitions = 0
                        self.disable()
                    elif(frame[1] == coap.codeINTERTALERROR):
                        type = (frame[0] & 48) >> 4                        
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = -2
                        self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                        self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                        self.reload_timeout()
                        self.disable_timeout() 
                        self.retransmitions = 0
                        self.disable()
                        
                        
                elif((frame[0] >> 4) == 4):
                    if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED
                    or frame[1] == coap.codeVALID):                        
                        type = (frame[0] & 48) >> 4    
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = frame[5+tkllen:]
                        self.response = response.Response(type, tkllen, code, mid, token, payload) 
                        self.sendACK(frame[2], frame[3])                        
                        self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                        self.reload_timeout()
                        self.disable_timeout() 
                        self.retransmitions = 0                    
                        self.disable()
                    elif(frame[1] == coap.codeINTERTALERROR):
                        type = (frame[0] & 48) >> 4                        
                        tkllen = frame[0] & 0x0F
                        code = frame[1]
                        mid = frame[2:4]
                        token = frame[4:(4+tkllen)]
                        payload = -2
                        self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                        self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                        self.reload_timeout()
                        self.disable_timeout() 
                        self.retransmitions = 0
                        self.disable()     
                           
                            
        elif (self.state == coap.wait2):         
            if ((frame[0] >> 4) != 4):
                if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED
                or frame[1] == coap.codeVALID):
                    type = (frame[0] & 48) >> 4 
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = frame[5+tkllen:]
                    self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                    self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                    self.reload_timeout()
                    self.disable_timeout()  
                    self.retransmitions = 0                 
                    self.disable()
                elif(frame[1] == coap.codeINTERTALERROR):
                    type = (frame[0] & 48) >> 4                        
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = -2
                    self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                    self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                    self.reload_timeout()
                    self.disable_timeout() 
                    self.retransmitions = 0
                    self.disable()
                        
            elif((frame[0] >> 4) == 4):
                if(frame[1] == coap.codeCONTENT or frame[1] == coap.codeCREATED
                or frame[1] == coap.codeVALID):                        
                    type = (frame[0] & 48) >> 4 
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = frame[5+tkllen:]
                    self.response = response.Response(type, tkllen, code, mid, token, payload) 
                    self.sendACK(frame[2], frame[3])  
                    self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                    self.reload_timeout()
                    self.disable_timeout()  
                    self.retransmitions = 0                    
                    self.disable() 
                elif(frame[1] == coap.codeINTERTALERROR):
                    type = (frame[0] & 48) >> 4                        
                    tkllen = frame[0] & 0x0F
                    code = frame[1]
                    mid = frame[2:4]
                    token = frame[4:(4+tkllen)]
                    payload = -2
                    self.response = response.Response(type, tkllen, code, mid, token, payload)                        
                    self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
                    self.reload_timeout()
                    self.disable_timeout() 
                    self.retransmitions = 0
                    self.disable()    
                      

    def sendACK(self, id1, id2):
        '''
            Método que envia mensagem de ACK para o servidor. Recebe como parametro
            dois bytes com o message id
        '''
        toBeSent = bytearray()
        toBeSent.append((coap.version << 6) | (coap.ACK << 4))
        toBeSent.append(coap.codeEMPTY)
        toBeSent.append(id1)
        toBeSent.append(id2)
        self.sock.sendto(toBeSent,self.servidor)
    
    def handle(self):
        self.handle_fsm(self.sock.recv(4096))
        

    def handle_timeout(self):
        if(self.retransmitions < coap.MAX_RETRANSMIT-1):
            self.sock.sendto(self.coapRequest, self.servidor)
            self._changeTimeoutValue(self.base_timeout*2)
            self.retransmitions = self.retransmitions + 1
            self.reload_timeout()
            self.enable_timeout()
            print(self.retransmitions)
            print(self.timeout)
        else:
            self._changeTimeoutValue(random.uniform(coap.ACK_TIMEOUT, coap.ACK_TIMEOUT * coap.ACK_RANDOM_FACTOR))
            self.reload_timeout()
            self.disable_timeout()
            self.response = response.Response(0, 0, 0, 0, 0, -1)
            self.state = coap.idle
            self.retransmitions = 0
            self.disable()
    
    def do_get(self, type, *uris): 
        '''
            Implementação do método GET.
            type: tipo da mensagem (CON, ACK ou NON)
            *uris: string(s) com a(s) uri(s) do recurso
        '''           
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


    def do_post(self, type, payload, *uris):
        '''
            Implementação do método POST.
            type: tipo da mensagem (CON, ACK ou NON)
            payload: payload da mensagem codificada com o protocol buffers
            *uris: string(s) com a(s) uri(s) do recurso
        '''  
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
        self.coapRequest.append(0x11) # (12-11  >>> codigo content format - codigo uri path)
        self.coapRequest.append(coap.octet_stream)    
        self.coapRequest.append(coap.end)
        for i in range (len(payload)):
            self.coapRequest.append(payload[i])
        print(self.coapRequest)        
        self.handle_fsm(self.coapRequest) 
        self.p.adiciona(self)
        self.p.despache()    
        return self.response

    def do_put(self, url, payload=None):
        pass
    
    def do_delete(self, url, payload=None):
        pass

    
  