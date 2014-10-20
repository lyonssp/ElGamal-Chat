import sys, socket, select, os

def chatDisplayMsg(username, msg = ""):
	return "<%s> %s" % (username, msg)

if(len(sys.argv) != 3):
		print("Usage: python chatClient.py <remote serverName> <remote host port>\n")
		sys.exit()

serverName = sys.argv[1]
serverPort = int(sys.argv[2])

username = raw_input('Please provide you temporary username: ')

#create socket
try:
	chatServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
	print("Socket not created.  Error Code: " + str(msg[0]))
	sys.exit()

listeners = [sys.stdin, chatServerSocket]

print("Connected to server\n")


#connect to the server
try:
	chatServerSocket.connect((serverName,serverPort))
except socket.error, msg:
	print("Error Code: %s\n") %os.strerror(msg[0])
	sys.exit()

#THIS IS WHERE TO MAKE KEY EXCHANGE

while 1:
	sys.stdout.write(chatDisplayMsg(username))
	sys.stdout.flush()

	readableSockets, writeableSockets, errorSockets = select.select(listeners, [], [])
	
	for socket in readableSockets:
			if socket == chatServerSocket:
					serverMsg, address = chatServerSocket.recvfrom(2048)
					if not serverMsg:
							print("Server is disconnected.\n\n")
							sys.exit()
					else:
							sys.stdout.write(chatDisplayMsg(address, serverMsg))
			else:
						msgToServer = sys.stdin.readline()
						chatServerSocket.send(chatDisplayMsg(username,msgToServer))

