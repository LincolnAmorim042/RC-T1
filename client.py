# Import socket module
import socket           
import sys

# Create a socket object
s = socket.socket()        
 
# Define the port on which you want to connect
port = int(sys.argv[1])              
 
# connect to the server on local computer
s.connect(('127.0.0.1', port))

# send the url to access and receive the message
url = input("Qual url a acessar? ")
s.send(url.encode())

# receive data from the server and decoding to get the string.
print (s.recv(1024).decode('utf-8'))

print (s.recv(1024).decode())
# close the connection
s.close()  