import datetime
import logging

import asyncio

import aiocoap.resource as resource
import aiocoap
from sensorapp_pb2 import Mensagem,Config,Dados,Sensor
from sensordb import SensorDB,Sensor,Placa,Amostra

class SensorApp(resource.Resource):

    GenericPeriod = 5000
    
    def __init__(self, dbname):
        super(SensorApp, self).__init__()
        self._n = 1
        self._db = SensorDB(dbname)
        self.content = "Recurso de testes para PTC !!\n\n"

    def __add_board(self, boardname, config):
        print('config')
        res = list(self._db.search(Placa, nome=boardname))
        if not res:
            placa = Placa(nome=boardname, periodo=SensorApp.GenericPeriod)
            self._db.insert(placa)
            res = list(self._db.search(Placa, nome=boardname))
        placa = res[0]
        for sensor in config.sensores:
            res = list(self._db.search(Sensor, nome=sensor,placa=placa.id))
            if not res:
                rec = Sensor(nome=sensor, placa=placa.id)
                self._db.insert(rec)

    def __add_data(self, board, dados):
        print('dados')
        for amostra in dados.amostras:            
            res = list(self._db.search(Sensor, nome=amostra.nome, placa=board.id))
            if res:
                sensor = res[0]
                sensor = Amostra(sensor=sensor.id, valor=amostra.valor, timestamp=amostra.timestamp)
                self._db.insert(sensor)
                
    def __list_boards(self):
        r = ''
        res = self._db.search(Placa)
        for placa in res:
            r += '%s (T=%d): ' % (placa.nome, placa.periodo)
            sensores = self._db.search(Sensor, placa=placa.id)
            for sens in sensores:
                r += '%s ' % sens.nome
        return r
                
            
    @asyncio.coroutine
    def render_get(self, request):
        content = self.__list_boards()
        content = content.encode("utf-8")
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=content)
        return response

    @asyncio.coroutine
    def render_post(self, request):
        print('POST payload: %s' % request.payload)
        msg = Mensagem()
        msg.ParseFromString(request.payload)
        print ('placa: ', msg.placa)
        submsg = msg.WhichOneof('msg')
        if submsg == 'config':
            self.__add_board(msg.placa, msg.config)
            msg.config.periodo = SensorApp.GenericPeriod
            payload = msg.SerializeToString()            
            return aiocoap.Message(code=aiocoap.CREATED, payload=payload)
        elif submsg == 'dados':
            res = list(self._db.search(Placa, nome=msg.placa))
            if not res: # desconhecida                
                return aiocoap.Message(code=aiocoap.NOT_FOUND)
            self.__add_data(res[0], msg.dados)
            return aiocoap.Message(code=aiocoap.VALID)
        else:
            return None

# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    root.add_resource(('ptc',), SensorApp('sensor.db'))

    asyncio.async(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
