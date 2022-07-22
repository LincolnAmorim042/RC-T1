from curses.ascii import isspace
import socket
import urllib3
import sys
import _thread
import ssl
import certifi

#controle das threads
def controlt(c):
  # recebe o request
  site = c.recv(1024).decode()
  print (addr, 'connecting to:\n', site, '\n')
  method = ""
  url = ""
  
  i=0
  while not(site[i].isspace()):
    method += site[i]
    i+=1
  i+=1
  while not(site[i].isspace()):
    url += site[i]
    i+=1
  version = site[-1]

  #trata o request
  match method:
    case "CONNECT":
      http = urllib3.PoolManager()
      resp = http.request("GET", url)
      c.send(resp.data)
    case "GET":
      http = urllib3.PoolManager()
      resp = http.request(method, url)
      c.send(resp.data)
    case "HEAD":
      http = urllib3.PoolManager()
      resp = http.request(method, url)
      val = str(resp.headers)
      c.send(val.encode())
    case "POST":
      http = urllib3.PoolManager(ca_certs=certifi.where())
      resp = http.request(method, url, fields={'example': 'post'})
      c.send(resp.data)
    #case "ADMIN"
      #match url:
        #case "FLUSH":
        #case "DELETE":
        #case "INFO":
        #case "MUDAR":
    case other:
      c.send('Error 501 Not Implemented!')
  i=0
  # fecha a conexao com o cliente
  c.close()

######################main###########################
urllib3.HTTPResponse.version = 10
# cria o socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
print ("Socket successfully created")
 
# reserva o port
port = int(sys.argv[1])

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binda o port
s.bind(('', port))
print ("socket binded to %s" %(port))
 
# coloca o socket em listen
s.listen(1)    
print ("socket is listening")           

#loop
while True:
# abre a conexao com o cliente
  c, addr = s.accept()
  print ('Got connection from', addr)

  #s = ssl.wrap_socket(s)
  _thread.start_new_thread(controlt,(c,))