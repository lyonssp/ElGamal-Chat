import socket, sys, select, os
from ElGamalModule import *
from Crypto.Cipher import AES
from AEShelpers import *
from Crypto import Random
import ast
import pdb

def serverAESsend(remoteSocket,decrypted_msg):
	try:
		AESkeyLen = len(clientAESkeys[remoteSocket])
		cipher = AES.new(clientAESkeys[remoteSocket])
		encrypted_msg = cipher.encrypt(pad_msg(decrypted_msg,AESkeyLen))
		remoteSocket.send(encrypted_msg)
	except Exception as e:
		displayException(serverAESsend.__name__,e)
	return sys.getsizeof(len(encrypted_msg))

def serverAESrecv(fromSocket):
		try:	
			encrypted_msg = fromSocket.recv(2048)
			if not encrypted_msg:
				return None
			else:
				cipher = AES.new(clientAESkeys[fromSocket])
				decrypted_msg = remove_pad_bytes(cipher.decrypt(encrypted_msg))
				return decrypted_msg
		except Exception as e:
			displayException(serverAESrecv.__name__,e)

#distribute an incoming message to all clients except the sender socket and serverSocket
#if a client refuses the message, close the client
def distributeMsg(sendSocket,msg):
	for client in clients:
			if client != sendSocket and client != serverSocket:
					try:
						numBytesSent = serverAESsend(client,msg)
						print("sent %d bytes to client: %s" % (numBytesSent,msg))
					except Exception as e:
						removeClient(client)
						displayException(distributeMsg.__name__,e)
						print("removed and closed client connection")

def addClient(connectionSocket):
		clients.append(connectionSocket)
		pubKeyString = "%d,%d,%d" %(p,g,b)
		#send public keys 
		connectionSocket.send(pubKeyString)
		(half_mask, encrypted_AESkey) = ast.literal_eval(connectionSocket.recv(2048))
		AESkey = eg_decrypt(encrypted_AESkey, half_mask, ElGamalSecKey, p)
		clientAESkeys[connectionSocket] = AESkey

def removeClient(connectionSocket):
		print("client List: %s" %clients)
		print("removing %s" %connectionSocket)
		clients.remove(connectionSocket)
		del clientAESkeys[connectionSocket]
		connectionSocket.close()

if len(sys.argv) != 3:
		print("Usage: python chatServer.py <port> <ElGamal Key Length in bits>\n")
		sys.exit()

clients = []
clientAESkeys = {}
ElGamalKeyLen = int(sys.argv[2])

if ElGamalKeyLen < 1024:
		print("WARNING: %d bit ElGamal keys can be insecure" %ElGamalKeyLen)

serverPort = int(sys.argv[1])
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

serverSocket.bind(('localhost',serverPort))
serverSocket.listen(1)
clients.append(serverSocket)

([p,g,b], ElGamalSecKey) = eg_setup(ElGamalKeyLen,1000)
print("Public ElGamal Keys [p,g,b]: [%s, %s, %s]" %(p,g,b))
print('The server is ready to receive.\n')

while 1:
	readableSockets, writeableSockets, errorSockets = select.select(clients, [], [])

	for socketToRead in readableSockets:
			#check for new connections in main server socket
			if socketToRead == serverSocket:
				connectionSocket, clientAddress = socketToRead.accept()
				addClient(connectionSocket)
				print(str(clientAddress) + " connected with AES key %s" %clientAESkeys[connectionSocket])
			#socketToRead must be connected to existing client
			else:
				try:
					clientMsg = serverAESrecv(socketToRead)
					if not clientMsg:
							removeClient(socketToRead)
					#confirm receipt and construct message to be broadcasted
					else:
							print("received client message: %s" % clientMsg)
							distributeMsg(socketToRead,clientMsg)
				except Exception as e:
					displayException("Main Server Loop",e)
