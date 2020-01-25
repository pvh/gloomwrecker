import socket

print('start')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 58888))
print('connected')
data = s.recv(1024)
print('Received', repr(data))
s.sendall(b's')
data = s.recv(1024)
s.close()
print('Received', repr(data))