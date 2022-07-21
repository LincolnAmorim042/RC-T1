from curses.ascii import isspace
import socket            
import urllib3
import sys
import _thread

# next create a socket object
s = socket.socket()        
print ("Socket successfully created")
 
# reserve a port on your computer
port = int(sys.argv[1])

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))
print ("socket binded to %s" %(port))
 
# put the socket into listening mode
s.listen(1)    
print ("socket is listening")           
 
def controlt(c):
  # receive the url to be accessed and send the message back
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
  i=0

  match method:
    case "GET":
      resp = http.request(method, url)
      c.send(resp.data)
    #case "FLUSH":
    #case "DELETE":
    #case "INFO":
    #case "MUDAR":
  
  # Close the connection with the client
  c.close()

# a forever loop until we interrupt it or
# an error occurs
while True:
 
# Establish connection with client.
  c, addr = s.accept()    
  print ('Got connection from', addr )

  http = urllib3.PoolManager()
  
  _thread.start_new_thread(controlt,(c,))
 
  
