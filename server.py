from curses.ascii import isspace
import socket
import urllib3
import sys
import _thread

BUFLEN=8192

#controle das threads
def controlt(c):
  # recebe o request
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
  
  if url=="":
    c.send(b'Incomplete Request')
    c.close()
    exit()
  #trata o request
  if not(req.find("1.1")==-1):
    method = "GET"
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
        #case "DELETE":
        #case "INFO":
        #case "MUDAR":
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