from curses.ascii import isspace
import socket
import urllib3
import sys
import _thread

BUFLEN=8192

#controle das threads
def controlt(c):
  # recebe o request
  req = ""
  req = c.recv(BUFLEN).decode()
  print (addr, 'requesting:\n', req)
  method = ""
  url = ""

  i=0
  while i<len(req) and not(req[i].isspace()):
    method += req[i]
    if i<len(req):
      i+=1
  i+=1
  while i<len(req) and not(req[i].isspace()):
    url += req[i]
    if i<len(req):
      i+=1
  i+=1
  if url=="":
    c.send(b'Incomplete Request')
    c.close()
    exit()

  if not(req.find("1.1")==-1) and req.find("ADMIN")==-1:
    method = "GET"
  if not(req.find("ADMIN")==-1):
    url = url.upper()
    req = req.upper()
  #trata o request
  match method:
    case "GET":
      http = urllib3.PoolManager()
      resp = http.request(method, url)
      c.send(resp.data)
    case "HEAD":
      http = urllib3.PoolManager()
      resp = http.request(method, url)
      val = str(resp.headers)
      c.send(val.encode())
    #case "POST":
      #http = urllib3.PoolManager(ca_certs=certifi.where())
      #resp = http.request(method, url, fields={'example': 'post'})
      #c.send(resp.data) 
    #case "ADMIN":
      #match url:
        #case "FLUSH":
          #limpa cache
        #case "DELETE":
          #nome = ""
          #while i<len(req) and not(req[i].isspace()):
            #nome += req[i]
            #i+=1
          #apaga esta caceta
        #case "INFO":
          #if not(req.find("INFO 0")==-1):
            #tamanho atual e lista de objetos do cache
        #case "MUDAR":
          #newsize = ""
          #while i<len(req) and not(req[i].isspace()):
            #newsize += req[i]
            #i+=1
          #tamanho cache = int(newsize)
    case other:
      c.send(b'Error 501 Not Implemented!')
  i=0
  # fecha a conexao com o cliente
  c.close()

######################main###########################
# cria o socket
port = int(sys.argv[1])

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)       
try:
  s.bind(('', port, 0, 0))
except socket.error:
  print("Erro no bind da porta: ", port)
  sys.exit(-1)
 
# coloca o socket em listen
s.listen(1)    
print ("socket is listening")           

#loop
while True:
# abre a conexao com o cliente
  c, addr = s.accept()
  print ('Got connection from', addr)

  _thread.start_new_thread(controlt,(c,))