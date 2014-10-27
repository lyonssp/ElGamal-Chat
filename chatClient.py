import sys, socket, select, os

def prompt():
	sys.stdout.write("<%s> " %username)
	sys.stdout.flush()

if(len(sys.argv) != 3):
		print("Usage: python chatClient.py <remote serverName> <remote host port>\n")
		sys.exit()

serverName = sys.argv[1]
serverPort = int(sys.argv[2])

username = input('Please provide you temporary username: ')

#create socket
try:
	chatServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except OSError as msg:
	print(msg)
	sys.exit()

listeners = [sys.stdin, chatServerSocket]

print("Connected to server\n")


#connect to the server
try:
	chatServerSocket.connect((serverName,serverPort))
except OSError as msg:
	print(msg)
	sys.exit()

#THIS IS WHERE TO MAKE KEY EXCHANGE

prompt()

while 1:

	readableSockets, writeableSockets, errorSockets = select.select(listeners, [], [])
	
	for socketToRead in readableSockets:
			if socketToRead == chatServerSocket:
					received = chatServerSocket.recv(2048).decode('utf-8')
					if not received:
							print("\rServer is disconnected.\n\n")
							sys.exit()
					else:
							sys.stdout.write("\r%s" %received)
							prompt()
			else:
						msgToServer = bytes("<%s> %s" % (username, sys.stdin.readline()),'utf-8')
						chatServerSocket.send(msgToServer)
						prompt()	
