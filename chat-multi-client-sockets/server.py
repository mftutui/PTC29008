import socket, select

def send_to_all (sock, message):
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				socket.close()
				connected_list.remove(socket)

def private_msg(sock):
	sock.send("\r\33[31m\33[1m Not the right sintaxe! \n To send a private message:'private;USERNAME:msgContent'\n \33[0m")

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

				#add name and address
				if name not in record.values():
					record[addr] = name
					suport[addr,conn] = name

					#server status msg
					print "Client (%s, %s) connected" % addr,"[",record[addr],"]" 

					conn.send("\33[32m\r\33[1m Welcome to chat room. Enter 'exit' anytime to left the chat\n\33[0m") 
					send_to_all(conn, "\33[32m\33[1m The user \33[34m\33[1m"+name+"\33[0m \33[32m\33[1mjoined the conversation \n\33[0m")
				else:
					#name already on record dict
					conn.send("\r\33[31m\33[1mUsername already taken!\n\33[0m")
					del record[addr]
					del suport[addr,conn]
					connected_list.remove(conn)
					conn.close()
					continue

			#data from client
			else:
				try:
					data_r = sock.recv(buffer)
					data = data_r[:data_r.index("\n")]
					
                    #geting from client sending the message
					ip,port = sock.getpeername()

					#server status msg
					print "Data [ %s ] received from:" % data,"[",record[addr],"]" 

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
					
					#if data is exactly "private"
					elif data == "private":
						private_msg(sock)
						
					# private message
					elif "private" in data:
						# recipient's name
						if (data.find(";") != -1) and (data.find(":") != -1):
							name_p = data[data.find(";")+1:data.find(":")]
							for addr, id_name in suport.items():
								if str(id_name) == name_p:
									msg = data[data.find(":")+1:]

									#server status msg
									print "Client (%s, %s) " % (ip,port),"[",record[(ip,port)],"] sending a private message to: [ %s ]" % name_p
									
									addr[1].send("private;"+record[(ip,port)]+":"+msg)
									continue	
							continue	
						else:
							private_msg(sock)
					else:
						msg = "\r\33[1m"+"\33[35m "+record[(ip,port)]+": "+"\33[0m"+data+"\n"
						send_to_all(sock,msg)
                # crt+c exit
				except:
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