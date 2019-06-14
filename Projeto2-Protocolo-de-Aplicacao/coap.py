from coapc import coap
from response import Response
from poller import Poller, Callback
import sensorapp_pb2
import sys,time
import random

class CoAPP(Callback):
    idle    = 0
    active  = 1
    def __init__(self):
        self.p = Poller()
        self.fd = None
        self.base_timeout = 10
        self.timeout = 10
        self.disable()
        self.disable_timeout()
        self.sensores = None
        self.placa = None
        self.state = CoAPP.idle
    
    def handle(self):
        pass
    
    def handle_timeout(self):
        msg = sensorapp_pb2.Mensagem()
        msg.placa = self.placa
        print(msg.placa)
        sensores = []
        for i in range (len(self.sensores)):
            sensor = sensorapp_pb2.Sensor()
            sensor.nome = self.sensores[i]
            sensor.valor = random.randint(-10,10)
            sensor.timestamp = int(time.time())
            sensores.append(sensor)

        msg.dados.amostras.extend(sensores)
        payload = msg.SerializeToString()
        print("Payload >>>",payload)
        r = coap("::1").do_post(coap.CON, payload ,'ptc')
        print(r.getPayload())
        if (r.getPayload() == -1):
            print("error")
            self.disable_timeout()
            self.disable()
            return False
    
    def configura(self, placa, periodo, *sensores):
        self.sensores = sensores
        self.placa = placa
        msg = sensorapp_pb2.Mensagem()
        msg.placa = placa
        msg.config.periodo = 10
        msg.config.sensores.extend(sensores)
        data = msg.SerializeToString()        
        payload = data
        r = coap("::1").do_post(coap.CON, payload ,'ptc')
        print(r.getPayload())
        if (r.getPayload() == -1):
            print("error")
            self.disable_timeout()
            self.disable()
            return False
        msg.ParseFromString(r.payload)
        self.base_timeout = int(msg.config.periodo/1000)
        return True

    def start(self):
        msg = sensorapp_pb2.Mensagem()
        msg.placa = self.placa
        print(msg.placa)
        sensores = []
        for i in range (len(self.sensores)):
            sensor = sensorapp_pb2.Sensor()
            sensor.nome = self.sensores[i]
            sensor.valor = random.randint(-10,10)
            sensor.timestamp = int(time.time())
            sensores.append(sensor)

        msg.dados.amostras.extend(sensores)
        payload = msg.SerializeToString()
        print("Payload >>>",payload)
        r = coap("::1").do_post(coap.CON, payload ,'ptc')
        if (r.getPayload() == -1):
            print("error")
            self.disable_timeout()
            self.disable()
            return False
        self.enable_timeout()
        self.enable()
        self.p.adiciona(self)
        self.p.despache()
        return False
        
a = CoAPP()
if (a.configura('placa2',10,'sensor A', 'sensor B')):
    while(a.start()):
        pass