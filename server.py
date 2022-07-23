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

  reqsplit = req.split()

  if len(reqsplit)==1:
    c.send(b'Incomplete Request')
    c.close()
    exit()

  if not(req.find("1.1")==-1) and req.find("ADMIN")==-1:
    reqsplit[0] = "GET"
  if not(req.find("ADMIN")==-1):
    reqsplit[1] = reqsplit[1].upper()
  #trata o request
  match reqsplit[0]:
    case "GET":
      http = urllib3.PoolManager()
      resp = http.request(reqsplit[0], reqsplit[1])
      c.send(resp.data)
    case "HEAD":
      http = urllib3.PoolManager()
      resp = http.request(reqsplit[0], reqsplit[1])
      val = str(resp.headers)
      c.send(val.encode())
    #case "POST":
      #http = urllib3.PoolManager()
      #resp = http.request(reqsplit[0], reqsplit[1], fields={reqsplit[2]: reqsplit[3]})
      #c.send(resp.data) 
    #case "ADMIN":
      #match reqsplit[1]:
        #case "FLUSH":
          #limpa cache
        #case "DELETE":
          #apaga esta caceta
        #case "INFO":
          #if reqsplit[2] == "0"):
            #salva tamanho atual e lista de objetos do cache
        #case "MUDAR":
          #tamanho cache = int(reqsplit[2])
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