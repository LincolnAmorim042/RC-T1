from fileinput import close
import socket
import urllib3
import sys
import _thread
import argparse
import logging
import logging.handlers

BUFLEN=8192

class LRUCache(object):
    def __init__(self,capacity):
        self.capacity = capacity
        self.cache = {}
        self.lru = {}
        self.tm = 0

    def get(self,key):  #se o dado existir no cache,retorna ele,se nao,retorna -1
        print("Pegando dados do cache")

        if key in self.cache: #se a chave existe no cache
            self.lru[key] = self.tm #variavel contadora de requisiçoes de dados vai somar 1
            self.tm = self.tm +1
            print("Cached")
            return self.cache[key]
        else:
            return -1 #dado nao ta no cache

    def set(self,key,value): #garantir que n vai atingir a capacidade maxima definida
        if len(self.cache) > self.capacity:  # se tiver cheio o cache,vai remover o mais antigo
            old_key = min(self.lru.keys(), key = lambda k: self.lru[k])

            # removendo
            self.cache.pop(old_key)  # remove o mais antigo do cache
            self.lru.pop(old_key)  # remove do LRU
        else:
            self.cache[key] = value
            self.lru[key] = self.tm
            self.tm = self.tm + 1

        print("LRU:{}".format(self.lru))
        print("Cache:{}".format(self.cache))


def Func(url, str1):
    sitehttp = url
    http = urllib3.PoolManager()
    response = http.request(str1, sitehttp)
    responsepronto = response.data
    verifica = caching.get(sitehttp)

    if(verifica == -1):
        result = responsepronto
        verifica = caching.set(sitehttp,result)

        print("Computando")
        #time.sleep(3)
        return result
    else:
        return verifica



# controle das threads
def controlt(c):
  global caching, tamcache, numhits, numfails
  # recebe o request
  msg = ""
  req = ""
  req = c.recv(BUFLEN).decode()
  reqsp = req.split()

  if len(reqsp)==1:
    c.send(b'Incomplete Request')
    c.close()
    exit()

  if "HTTP/1.1" in reqsp and not("ADMIN" in reqsp):
    reqsp[0] = "GET"
  if "ADMIN" in reqsp:
    reqsp[1] = reqsp[1].upper()

  # trata o request
  if ("ADMIN" in reqsp):
    #acha a resposta pro request no arquivo
    numhits+=1
    msg = str(_thread.get_native_id())+"\tHIT\t"+reqsp[1]
    logging.info(msg)
    # c.send(caching.line[1]) 
  else:
    match reqsp[0]:
      case "GET":
        numfails+=1
        msg = str(_thread.get_native_id())+"\tADD\t"+reqsp[1]
        logging.info(msg)
        # http = urllib3.PoolManager()
        # resp = http.request(reqsp[0], reqsp[1])
        # c.send(resp.data)
        c.send(Func(reqsp[1],reqsp[0]))
        #if caching.sizeof()<tamcache:
          #salva no cache
      case "HEAD":
        msg = str(_thread.get_native_id())+"\tADD\t"+reqsp[1]+" headers"
        logging.info(msg)
        http = urllib3.PoolManager()
        resp = http.request(reqsp[0], reqsp[1])
        head = str(resp.headers)
        c.send(head.encode())
        #if caching.sizeof()<tamcache:
          #salva no cache
      case "ADMIN":
        match reqsp[1]:
          case "FLUSH":
            msg = str(_thread.get_native_id())+"\tFLUSH\tRequested"
            logging.info(msg)
            caching = close()
            caching = open("cache.txt", "w+")
          #case "DELETE":
            #apaga reqsp[2]
          case "INFO":
            match reqsp[2]:
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
            msg = str(_thread.get_native_id())+"\tCHSIZE\told: "+str(tamcache/1024)+"\tnew: "+reqsp[2]
            logging.info(msg)
            tamcache = int(reqsp[2])*1024
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
caching = LRUCache(capacity=tamcache)

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