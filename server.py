from fileinput import close
import socket
import urllib3
import sys
import _thread
import argparse
import logging
import logging.handlers

BUFLEN=8192

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
  if not("ADMIN" in reqsp) and req in caching:
    #acha a resposta pro request no arquivo
    numhits+=1
    msg = str(_thread.get_native_id())+"\tHIT\t"+reqsp[1]
    logging.info(msg)
    c.send(caching.line[1]) 
  else:
    match reqsp[0]:
      case "GET":
        numfails+=1
        msg = str(_thread.get_native_id())+"\tADD\t"+reqsp[1]
        logging.info(msg)
        http = urllib3.PoolManager()
        resp = http.request(reqsp[0], reqsp[1])
        c.send(resp.data)
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

caching = open("cache.txt", "w+")

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