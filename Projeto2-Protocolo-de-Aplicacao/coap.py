#!/usr/bin/python3
# -*- coding: utf-8 -*- 
__author__ = "Paulo Sell e Maria Fernanda Tutui"

from coapc import coap
from response import Response
from poller import Poller, Callback
import sensorapp_pb2
import sys,time
import random

class CoAPP(Callback):
    '''
        Classe responsável por utilizar os métodos da classe coap e implementar o protocolo
        de aplicação (registro da placa no servidor e troca de dados dos sensores)
    '''

    def __init__(self):
        self.p = Poller()
        self.fd = None
        self.base_timeout = 10
        self.timeout = 10
        self.disable()
        self.disable_timeout()
        self.sensores = None
        self.placa = None
    
        
    
    def handle(self):
        pass
    
    def handle_timeout(self):
        '''
            Método para transmitir os dados de sensores a cada timeout
        '''
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
        if (r.getPayload() == -1 or r.getPayload() == -2):
            print("error", r.getPayload())
            self.disable_timeout()
            self.disable()
            return False
    
    def configura(self, placa, periodo, *sensores):
        '''
            Método que faz o registro da placa no servidor
            Recebe como parâmetros:
            placa: string representando o nome da unidade de aquisição de dados
            periodo: inteiro com o intervalo de tempo de retransmissão desejado pelo usuário
            *sensores: listra de string com os nomes dos sensores que irão ser utilizados

            Retorna True se a requisição for bem sucedida. Retorna False caso haja erro na configuração
        '''
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
        if (r.getPayload() == -1 or r.getPayload() == -2):
            print("error", r.getPayload())
            self.disable_timeout()
            self.disable()
            return False
        msg.ParseFromString(r.getPayload())
        self.base_timeout = int(msg.config.periodo/1000)
        return True

    def start(self):
        '''
            Método que inicia a troca de mensagens com os dados de sensores. Faz o primeiro envio
            e após deixa a retransmissão a cargo da classe Poller
        '''
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
        if (r.getPayload() == -1 or r.getPayload() == -2):
            print("error", r.getPayload())
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
    a.start()
        
