import sqlite3
import string
from collections import OrderedDict

class Record:

  Tabela = ''
  Attrs = OrderedDict()
  Attrs['id']=0
  Key = 'id'
  Index = ()

  def __init__(self, **args):    
    self.attrs = OrderedDict()
    self.attrs.update(self.Attrs)
    self.Tabela = self.__class__.__name__

    try:
      dbdata = args['values']
      if len(dbdata) != len(self.Attrs): 
        raise ValueError('incorrect number of values: expected %d, found %d' % (len(self.Attrs), len(dbdata)))
      n = 0
      for k in self.attrs:
        self.attrs[k] = dbdata[n]
        n+=1
    except KeyError:
      pass
    for k in args.keys():
      if k == 'values': continue
      if not k in self.Attrs: raise KeyError('unknown column %s' % k)
      self.attrs[k] = args[k]
    self.changed = []

  def __nonzero__(self):
    return self.id != 0

  def __getattr__(self, k):
    try:
      v = self.attrs[k]
      if v == None: return 'null'
      return v
    except:
      return self.__dict__[k]

  def __dir__(self):
    return self.__dict__.keys() + self.attrs.keys()

  def __setattr__(self, k, v):
    if not k in self.Attrs:
      self.__dict__[k] = v
    else:
      self.attrs[k] = v
      if not k in self.changed: self.changed.append(k)

  def set_update(self, k):
    if not k in self.attrs: raise KeyError(k)
    if not k in self.changed: self.changed.append(k)
    
  def values(self):
    e = []
    n = 0
    for k in self.Attrs:
      v = self.attrs[k]
      if v == None:
        v = 'null'
      elif type(v) in [type(''), type(u'')]:
        v = r'"%s"' % v
      else:
        v = r'%d' % v
      e.append(v)
      n += 1
    return ','.join(e)

  def selector(self):
    val = self.attrs[self.Key]
    if val == None: raise ValueError('unitialized data')
    if type(val) in [type(''), type(u'')]:
      return r'%s="%s"' % (self.Key, val)
    return r'%s=%d' % (self.Key, val)

  def update(self):
    if not self.changed: return ''
    e = []
    for k in self.changed:
      v = self.attrs[k]
      if type(v) in [type(''), type(u'')]:
        v = r'%s="%s"' % (k, v)
      else:
        v = r'%s=%d' % (k, v)
      e.append(v)
    return ','.join(e)

  @classmethod
  def __get_attr__(cls, k):
    val = cls.Attrs[k]
    tipo = type(val)
    if tipo == type(1): tname = 'integer'
    elif tipo == type(''): tname = 'text'
    elif tipo == type(True): tname = 'integer'
    elif tipo == type(0.1): tname = 'real'
    else: raise ValueError('tipo %s desconhecido' % tipo)
   
    if k == cls.Key: tname = '%s primary key' % tname

    return tname

  @staticmethod
  def init_attrs():
    attrs = OrderedDict()
    attrs.update(Record.Attrs)
    return attrs

  @classmethod
  def get_schema(cls):
    schema = []
    r = 'create table %s (' % cls.__name__
    attrs = []
    for k in cls.Attrs:
      attrs.append('%s %s' % (k, cls.__get_attr__(k)))
    r += ','.join(attrs)
    r += ')'
    schema.append(r)
    for k in cls.Index:
      if type(k) != type(''):
        k = ','.join(list(k))
      schema.append('create index ind_%s_%s on %s (%s)' % (cls.__name__, k, cls.__name__, k))
    return schema

  @classmethod
  def get_name(cls):
    return cls.__name__

  def cleanup(self,  db):
      pass
      
  def __str__(self):
      return repr(self)
      
  def __repr__(self):
    r = '<%s: ' % self.Tabela
    l = []
    for k in self.attrs:
      l.append('%s=%s' % (k, self.attrs[k]))
    r += '%s>' % ','.join(l)
    return r

class MyDB:

  SQL_simple_select = 'select * from %s'
  SQL_select = 'select * from %s where %s'
  SQL_update = 'update %s set %s where %s'
  SQL_delete = 'delete from %s where id=%d'
  SQL_insert = 'insert or replace into %s values(%s)'
  SQL_insert_default = 'insert or replace into %s default values'
  Tabelas = []

  def __init__(self, path):
    self.closed = True
    self.path = path
    self.open()
    c = self.db.cursor()
    for tab in self.Tabelas:
      try:
        c.execute('select id from %s limit 1' % tab.get_name())
      except Exception as e:
        #print('--->', e)
        for cmd in tab.get_schema():
          #print(cmd)
          c.execute(cmd)
        self.db.commit()
    c.close()

  def __genexpr__(self, attr, val):
    if type(val) in [type(''), type(u'')]:
      if attr == 'expr':
        pass
      elif val.find(r'%') < 0:
        val = '%s="%s"' % (attr, val)
      else:
        val = '%s like "%s"' % (attr, val)
    else:
      val = '%s=%d' % (attr, val)
    return val

  def open(self):
    if self.closed:
      self.db = sqlite3.connect(self.path)
      self.closed = False

  # Faz uma consulta com base em data_class, e com expressao
  # composta por attrs. A expressao faz uma conjuncao de igualdades.
  def search(self, data_class, **attrs):
    expr = []
    order = ''
    limit = ''
    asc=True
    for attr in attrs:
      val = attrs[attr]
      if attr == 'order':
        order = val
      elif attr == 'limit':
        limit = val
      elif attr == 'asc':
        asc=val
      else:
        if type(val) == type([]):
          if not val: continue
          val = map(lambda x: self.__genexpr__(attr, x), val)
          val = ' or '.join(val)
        else:
          val = self.__genexpr__(attr, val)
        expr.append(val)
    expr = ' and '.join(expr)
    has_filter = (expr != '')
    if order:
      expr += ' order by %s' % order
      if asc: expr += ' asc'
      else: expr += ' desc'
    if limit:
      expr += ' limit %d' % limit
    expr = expr.strip()
    c = self.db.cursor()
    if not has_filter:
      expr = '%s %s' % (self.SQL_simple_select % data_class.get_name(), expr)
    else:
      expr = self.SQL_select % (data_class.get_name(), expr)
    #print expr
    c.execute(expr)
    r = c.fetchall()
    c.close()
    r = map(lambda x: data_class(values=x), r)
    return r

  def update(self, obj, extra=''):
    expr = self.SQL_update % (obj.Tabela, obj.update(), obj.selector())
    if extra:
      expr = '%s and %s' % extra
    c = self.db.cursor()
    c.execute(expr)
    self.db.commit()
    c.close()

  def insert(self, obj, search=[]):
    obj.attrs[obj.Key] = None
    expr = self.SQL_insert % (obj.Tabela, obj.values())
    c = self.db.cursor()
    c.execute(expr)
    self.db.commit()
    c.close()
    if search:
      args = {}
      for k in search:
        args[k] = getattr(obj, k)
      r = apply(self.search, (obj.__class__,), args)
      return r[0]

  def delete(self,  obj):
      expr = self.SQL_delete % (obj.Tabela,  obj.id)
      c = self.db.cursor()
      c.execute(expr)
      self.db.commit()
      c.close()
      obj.cleanup(self)
      
  def close(self):
    self.db.close()
    self.closed = True
 
