from curses.ascii import isspace
import socket            
import urllib3
import sys
import _thread
import ssl

# cria o socket
s = socket.socket()        
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

  #trata o request
  match method:
    case "CONNECT":
      url1 = ""
      i=0
      while not(url[i]==':'):
        url1 += url[i]
        i+=1
      i=0
      s.connect((url1, 443))
      request = b'GET', url1, 'HTTP/1.1\n\n'
      c.send(request)
    case "GET":
      resp = http.request(method, url)
      c.send(resp.data)
    case "HEAD":
      resp = http.request(method, url)
      c.send(resp.headers)
    #case "POST":

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

#loop
while True:
# abre a conexao com o cliente
  c, addr = s.accept()    
  print ('Got connection from', addr)

  http = urllib3.PoolManager()
  s = ssl.wrap_socket(s)
  _thread.start_new_thread(controlt,(c,))
 
  
