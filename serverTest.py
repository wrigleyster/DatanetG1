#!/usr/bin/python

import socket

HOST = ''
PORT = 3456

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print "Connected from ", addr

while 1:
    data = conn.recv(1024)
    if not data: break
    conn.sendall('100 ' + 'connected ' + data)
    
    print data
    
conn.close()
