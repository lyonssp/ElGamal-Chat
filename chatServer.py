import socket, sys, select, os

def chatDisplayMsg(username, msg):
	return "<%s> %s " %(username,msg)

#distribute an incoming message to all clients except the sender sock and serverSocket
#if a client refuses the message, close the client
def distributeMsg(sendSocket,msg):
	for client in clients:
			if client != sendSocket and client != serverSocket:
					try:
						client.send(msg)
						print("sent message to client")
					except:
						client.close()
						clients.remove(client)
						print("removed and closed client connection")

if len(sys.argv) != 2:
		print("Usage: python chatServer.py <port>\n")
		sys.exit()

clients = []

serverPort = int(sys.argv[1])
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

serverSocket.bind(('localhost',serverPort))
serverSocket.listen(1)
clients.append(serverSocket)

print 'The server is ready to receive.\n'

while 1:
	readableSockets, writeableSockets, errorSockets = select.select(clients, [], [])
	
	for socketToRead in readableSockets:
			#check for new connections in main server socket
			if socketToRead == serverSocket:	
				connectionSocket, clientAddress = serverSocket.accept()
				clients.append(connectionSocket)
				print(clientAddress)
			#socketToRead must be connected to existing client
			else:
				try:
					clientMsg, clientAddr = socketToRead.recvfrom(2048)
					print("received client message: %s") %clientMsg
					distributeMsg(socketToRead,clientMsg)
				except socket.error, msg:
					print("Error %s") %os.strerror(msg[0])
					socketToRead.close()
					clients.remove(socket)

connectionSocket.close()

