import socket
import urllib3
import sys
import _thread
import argparse
import logging
import logging.handlers

BUFLEN=8192

class LRUCache(object):
  def __init__(self,tam):
    self.tam = tam
    self.cache = {}
    self.lru = {}
    self.tm = 0
  def get(self,key):  # se o dado existir no cache,retorna ele,se nao,retorna -1
    if key in self.cache:
      self.lru[key] = self.tm # variavel contadora de requisiçoes de dados vai somar 1
      self.tm = self.tm +1
      return self.cache[key]
    else:
      return -1
  def set(self,key,value): # garantir que n vai atingir a capacidade maxima definida
    if len(self.cache) > self.tam:  # se tiver cheio o cache,vai remover o mais antigo
      old_key = min(self.lru.keys(), key = lambda k: self.lru[k])
      self.cache.pop(old_key)  # remove o mais antigo do cache
      self.lru.pop(old_key)  # remove do LRU
    else:
      self.cache[key] = value
      self.lru[key] = self.tm
      self.tm = self.tm + 1


def testcache(met,url):
  global caching, tamcache, numhits, numfails
  sitehttp = url
  http = urllib3.PoolManager()
  response = http.request(met, sitehttp)
  responsepronto = response.data
  verifica = caching.get(sitehttp)

  if(verifica == -1):
    result = responsepronto
    verifica = caching.set(sitehttp,result)
    numfails+=1
    msg = str(_thread.get_native_id())+"\tADD\t"+url
    logging.info(msg)
    return result
  else:
    numhits+=1
    msg = str(_thread.get_native_id())+"\tHIT\t"+url
    logging.info(msg)
    return verifica

# controle das threads
def controlt(c):
  global caching, tamcache, numhits, numfails
  # recebe o request
  msg = ""
  req = ""
  req = c.recv(BUFLEN).decode()
  reqsplit = req.split()

  if len(reqsplit)==1:
    c.send(b'Incomplete Request')
    c.close()
    exit()

  if "HTTP/1.1" in reqsplit and not("ADMIN" in reqsplit):
    reqsplit[0] = "GET"
  if "ADMIN" in reqsplit:
    reqsplit[1] = reqsplit[1].upper()

  # trata o request 
  match reqsplit[0]:
    case "GET":
      c.send(testcache(reqsplit[0],reqsplit[1]))
    case "ADMIN":
      match reqsplit[1]:
        case "FLUSH":
          msg = str(_thread.get_native_id())+"\tFLUSH\tRequested"
          logging.info(msg)
            
        #case "DELETE": #TODO
          #apaga reqsplit[2] do cache
        case "INFO":
          match reqsplit[2]: #TODO
            case "0": # salva tamanho atual e lista de objetos do cache
              msg = str(_thread.get_native_id())+"\tDUMP\tDump Start"
              logging.info(msg)
              msg = str(_thread.get_native_id())+"\tDUMP\tSize "+str(tamcache/1024)
              logging.info(msg)
            #case "1": # salva os não-expirados
            case "2":
              msg = str(_thread.get_native_id())+"\tNúmero Total de Pedidos:\t"+str(numpedidos)
              logging.info(msg)
              msg = str(_thread.get_native_id())+"\tNúmero Total de Hits:\t"+str(numhits)
              logging.info(msg)
              msg = str(_thread.get_native_id())+"\tNúmero Total de Fails:\t"+str(numfails)
              logging.info(msg)
              msg = str(_thread.get_native_id())+"\tTamanho Médio das Páginas em Cache:\t"+str(numfails/tamcache)
              logging.info(msg)
        case "CHANGE":
          msg = str(_thread.get_native_id())+"\tCHSIZE\told: "+str(tamcache/1024)+"\tnew: "+reqsplit[2]
          logging.info(msg)
          caching.tam=int(reqsplit[2])*1024
    case other:
      c.send(b'Error 501 Not Implemented!')
  i=0
  # fecha a conexao com o cliente
  c.close()

######################main###########################
parser = argparse.ArgumentParser(prog='python3',usage='%(prog)s path [options]')
parser.add_argument('-c', type=int, help="tamanho do cache em kb")
parser.add_argument('-p', type=int, help="numero do port", required=True)
parser.add_argument('-l', type=str, help="nome do arquivo de log")

argv = parser.parse_args()

port = argv.p

if not(argv.c==None):
  tamcache = argv.c*1024
  print("Tamanho do cache definido como:", tamcache)
else: 
  tamcache = 1000*1024
  print("Tamanho do cache definido como:", tamcache)
if not(argv.l==None):
    nomelog = argv.l
else:
    nomelog = "log.txt"
logging.basicConfig(level=logging.INFO,format="%(message)s",handlers=[logging.FileHandler(nomelog, mode="w"),logging.StreamHandler()])

# caching = open("cache.txt", "w+")
caching = LRUCache(tam=tamcache)

# cria o socket
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)       
try:
  s.bind(('', port, 0, 0))
except socket.error:
  print("Erro no bind da porta:", port)
  sys.exit(-1)
print ("Port definido como:", port)

# coloca o socket em listen
s.listen(1)    
print ("Socket is listening")           
numpedidos=0
numhits=0
numfails=0
# loop
while True:
# abre a conexao com o cliente
  c, addr = s.accept()
  msg='Got connection from '+ str(addr)
  logging.info(msg)
  numpedidos+=1
  _thread.start_new_thread(controlt,(c,))
