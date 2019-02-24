import socket, select

def send_to_all (sock, message):
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				socket.close()
				connected_list.remove(socket)

def private_guide():
	sock.send("\r\33[31m\33[1mWrong sintaxe! \n To send a private message use:\33[0m \33[34m\33[1m'p.USERNAME:msgContent'\n\33[0m")

def check_name_list():
	if name not in record.values():
		record[addr] = name
		suport[addr,conn] = name

		#server status msg
		print "Client (%s, %s) connected" % addr,"[",record[addr],"]" 

		conn.send("\33[32m\r\33[1m Welcome to chat room. Enter 'exit' anytime to left. \n\33[0m") 
		send_to_all(conn, "\33[32m\r\33[1m The user \33[34m\33[1m"+name+"\33[0m \33[32m\33[1mjoined the conversation. \n\33[0m")
	else:
		conn.send("\r\33[31m\33[1mUsername already taken! \n\33[0m")
		del record[addr]
		del suport[addr,conn]
		connected_list.remove(conn)
		conn.close()

def show_users(sock, suport, your_name):
	if len(suport) > 1 :
		sock.send("\33[32m\r\33[1mConnected users: \n\33[0m")
		for addr, id_name in suport.items():
			if your_name != id_name:
				sock.send("\33[32m\r\33[1m - "+id_name+"\n\33[0m")
	else:
		sock.send("\33[31m\r\33[1mThere are no users connected besides you.\n\33[0m")

def private_msg(data, sock, suport):
	print "data que chegou: ", data
	print data.find(".") + "\n"
	print data.find(":") + "\n"	
	print "agora chegou no IF"
	i = 0
	
	if (data.find(".") != -1) and (data.find(":") != -1):
		name_p = data[data.find(".")+1:data.find(":")]
		for addr, id_name in suport.items():
			if str(id_name) == str(name_p):
				addr_p = addr
				i = 1
		if i == 1:
			msg = data[data.find(":")+1:]
			print "Client (%s, %s) " % (ip,port),"[",record[(ip,port)],"] sending a private message to: [ %s ]" % name_p
			addr_p[1].send("\33[34m\r\33[1mPrivate message from "+record[(ip,port)]+"\33[0m:"+msg+ "\n")	
		else:
			sock.send("\33[31m\r\33[1m The user \33[34m\33[1m"+name_p+"\33[0m \33[31m\33[1mis not connected. \n\33[0m")
	else:
		private_guide(sock)

		
if __name__ == "__main__":
	name = ""
	#dictionary to store address corresponding to username
	record = {}
	suport = {}
	#list to keep track of socket descriptors
	connected_list = []

	#time used on recv
	buffer = 4096 
	port = 5002

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("localhost", port))
	server_socket.listen(5)

	#add a socket object to the connections list
	connected_list.append(server_socket)

	#server status msg
	print "\33[32m \tSERVER WORKING \33[0m" 

	while 1:
		rList,wList,error_sockets = select.select(connected_list,[],[])

		for sock in rList:
			#creating a new connection 
			if sock == server_socket:
				#infos
				conn, addr = server_socket.accept() 
				name = conn.recv(buffer)
				connected_list.append(conn) 
				record[addr] = ""
				suport[addr,conn] = ""
				check_name_list()

			#data from client
			else:
				try:
					data_r = sock.recv(buffer)
					data = data_r[:data_r.index("\n")]
					ip,port = sock.getpeername()
					print "Data [ %s ] received from:" % data,"[",record[(ip,port)],"]" 

					if data == "exit":
						msg = "\r\33[1m"+"\33[31m "+record[(ip,port)]+" left the conversation \n\33[0m"
						send_to_all(sock,msg)

						#server status msg
						print "Client (%s, %s) is offline" % (ip,port)," [",record[(ip,port)],"]"
						
						del record[(ip,port)]
						del suport[(ip,port),conn]
						connected_list.remove(sock)
						sock.close()
						continue
					elif data == "private":
						private_guide()
					elif "p." in data:
						private_msg(data, sock, suport)
					elif data == "show users":
						show_users(sock, suport, record[(ip,port)])
					else:
						msg = "\r\33[1m"+"\33[35m "+record[(ip,port)]+": "+"\33[0m"+data+"\n"
						send_to_all(sock,msg)
				except:
					print "-------------------------XXXXXXXXXX-------------------------"
					(ip,port) = sock.getpeername()
					send_to_all(sock, "\r\33[31m \33[1m"+record[(ip,port)]+" left the conversation unexpectedly\33[0m\n")

					#server status msg	
					print "Client (%s, %s) is offline (error)" % (ip,port)," [",record[(ip,port)],"]\n"

					del record[(ip,port)]
					del suport[(ip,port),conn]
					connected_list.remove(sock)
					sock.close()
					continue

	server_socket.close()

	# pensar em uma forma de pedir para digitar o nome novamente se ja estiver na lista e nao derrubar a conexao
	# tratar dados igual a nada