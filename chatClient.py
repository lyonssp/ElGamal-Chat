import pdb
import sys, socket, select, os
from ElGamalModule import *
from Crypto.Cipher import AES
from Crypto import Random
from AEShelpers import *

def clientAESsend(remoteSocket,msg):
	try:
		encrypted_msg = cipher.encrypt(pad_msg(msg,AESkeyLen))
		remoteSocket.send(encrypted_msg)
		return sys.getsizeof(encrypted_msg)
	except Exception as e:
		displayException(clientAESsend.__name__,e)
	

def clientAESrecv(fromSocket):
	try:
		encrypted_msg = fromSocket.recv(2048)
		if not encrypted_msg:
			print("received blank message from server.  Disconnecting.")
			sys.exit()
		else:
			decrypted_msg = remove_pad_bytes(cipher.decrypt(encrypted_msg))
			return decrypted_msg
	except Exception as e:
		displayException(clientAESrecv.__name__,e)

def prompt():
		sys.stdout.write("<%s> " %username)
		sys.stdout.flush()

if(len(sys.argv) != 4):
		print("Usage: python chatClient.py <remote serverName> <remote host port> <AES key length in bytes>\n")
		sys.exit()

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
AESkeyLen = int(sys.argv[3])

username = raw_input('Please provide you temporary username: ')

#create server socket object
try:
	chatServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except Exception as e:
	displayException("Server Socket Creation",e)
	sys.exit()


#connect to the server
try:
	chatServerSocket.connect((serverName,serverPort))
except Exception as e:
	displayException("Server Socket Connection",e)
	sys.exit()

#retrieve public keys
print("Getting Public Keys from server...")
try:
	pubKeyMsg = chatServerSocket.recv(2048)
	[p,g,b] = map(long,pubKeyMsg.split(','))
	print("Public Keys from Server [p,g,b]: [%d, %d, %d]" %(p,g,b))
except:
	displayException("Retrieving Public Keys",e)
	sys.exit()

#send AES secret key using ElGamal-encrypted channel
AESkey = os.urandom(AESkeyLen)
chatServerSocket.send(eg_msg_mask_pair(AESkey,p,g,b))

#client will use this cipher for all encryption/decryption
cipher = AES.new(AESkey)

#listen on these streams
listeners = [sys.stdin, chatServerSocket]

prompt()

while 1:

	readableSockets, writeableSockets, errorSockets = select.select(listeners, [], [])
	
	for socketToRead in readableSockets:
			if socketToRead == chatServerSocket:
					received = clientAESrecv(socketToRead)
					sys.stdout.write("\r%s" %received)
					sys.stdout.flush()
					prompt()
			else:
						msgToServer = "<%s> %s" % (username, sys.stdin.readline())
						clientAESsend(chatServerSocket,msgToServer)
						prompt()	
