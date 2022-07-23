from curses.ascii import isspace
import socket
import urllib3
import sys
import _thread
import argparse

BUFLEN=8192

#controle das threads
def controlt(c):
  # recebe o request
  req = ""
  req = c.recv(BUFLEN).decode()
  print (addr, 'requesting:\n', req)

  reqsp = req.split()

  if len(reqsp)==1:
    c.send(b'Incomplete Request')
    c.close()
    exit()

  if "HTTP/1.1" in reqsp and not("ADMIN" in reqsp):
    reqsp[0] = "GET"
  if "ADMIN" in reqsp:
    reqsp[1] = reqsp[1].upper()
  
  #trata o request
  match reqsp[0]:
    case "GET":
      http = urllib3.PoolManager()
      resp = http.request(reqsp[0], reqsp[1])
      c.send(resp.data)
    case "HEAD":
      http = urllib3.PoolManager()
      resp = http.request(reqsp[0], reqsp[1])
      val = str(resp.headers)
      c.send(val.encode())
    #case "POST":
      #http = urllib3.PoolManager()
      #resp = http.request(reqsp[0], reqsp[1], fields={reqsp[2]: reqsp[3]})
      #c.send(resp.data) 
    #case "ADMIN":
      #match reqsp[1]:
        #case "FLUSH":
          #limpa cache
        #case "DELETE":
          #apaga reqsp[2]
        #case "INFO":
          #if reqsp[2] == "0": # salva tamanho atual e lista de objetos do cache
          #if reqsp[2] == "1": # salva os não-expirados
        #case "MUDAR":
          #argv.c = int(reqsp[2])
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
parser.add_argument('-a', type=str, help="nome do arquivo do algoritmo")

argv = parser.parse_args()

port = argv.p

# cria o socket
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

# loop
while True:
# abre a conexao com o cliente
  c, addr = s.accept()
  print ('Got connection from', addr)

  _thread.start_new_thread(controlt,(c,))