import sys
from enum import Enum
if sys.version_info.major < 3:
  from mydb import Record,MyDB
else:
  from mydb3 import Record,MyDB
import datetime

class Sensor(Record):

  Attrs = Record.init_attrs()
  Attrs['nome']=''
  Attrs['placa']=0
  Index = ('nome','placa')

class Placa(Record):

  Attrs = Record.init_attrs()
  Attrs['nome']=''
  Attrs['periodo']=0
  Index = ('nome',)

class Amostra(Record):

  Attrs = Record.init_attrs()
  Attrs['valor']=''
  Attrs['timestamp']=0
  Attrs['sensor']=0
  Index = ('sensor','timestamp')
          
class SensorDB(MyDB):

  Tabelas = (Sensor,Placa,Amostra)
        
      
