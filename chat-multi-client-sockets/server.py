# https://github.com/mftutui/PTC29008

import socket, select

def send_to_all (sock, message):
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				socket.close()
				connected_list.remove(socket)

def private_guide(sock):
	sock.send("\r\33[31m\33[1mWrong sintaxe! \n To send a private message use:\33[0m \33[34m\33[1m'p.USERNAME:msgContent'\n\33[0m")

def check_name_list(conn, record, suport, connected_list):
	if name not in record.values():
		record[addr] = name
		suport[addr,conn] = name

		#server status msg
		print "Client (%s, %s) connected" % addr,"[",record[addr],"]"

		welcome_rules(conn)
		
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
			addr_p[1].send("\33[34m\r\33[1mPrivate message from "+record[(ip,port)]+": \33[0m"+msg+ "\n")
			sock.send("\33[32m\r\33[1mYour private message was sended.\n\33[0m")
		else:
			sock.send("\33[31m\r\33[1m The user \33[34m\33[1m"+name_p+"\33[0m \33[31m\33[1mis not connected. \n\33[0m")
	else:
		private_guide(sock)

def welcome_rules(conn):
	conn.send("\33[32m\r\33[1m Welcome to chat room! \n\33[0m")
	conn.send("\33[32m\r\33[1m - Enter 'exit' anytime to left. \n\33[0m")
	conn.send("\33[32m\r\33[1m - Enter 'show users' to see who is online. \n\33[0m")
	conn.send("\33[32m\r\33[1m - To send a private message use:\33[0m \33[34m\33[1m'p.USERNAME:msgContent'\n\33[0m")
	send_to_all(conn, "\33[32m\r\33[1m The user \33[34m\33[1m"+name+"\33[0m \33[32m\33[1mjoined the conversation. \n\33[0m")

def exit_chat(sock, name_ex, record, suport, connected_list):
	for addr, name in suport.items():
		if addr[1] == sock:
			msg = "\r\33[1m"+"\33[31mThe user "+name_ex+" left the conversation. \n\33[0m"
			print "Client (%s, %s) is offline (error)" % (ip,port)," [",record[(ip,port)],"]"
			send_to_all(sock, msg)
			for item in connected_list:
				if item == sock:
					connected_list.remove(sock)
			for	ipportasock, nome  in suport.items():
				if ipportasock[1] == sock:
					del suport[ipportasock]
			for ipportasock2, nome2 in record.items():
				if nome2 == name_ex:
					del record[ipportasock2]
			sock.send("exit_chat")

if __name__ == "__main__":
	name = ""
	record = {}
	suport = {}
	connected_list = []

	#time used on recv
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("localhost", port))
	server_socket.listen(5)

	#add a socket object to the connections list
	connected_list.append(server_socket)

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
				check_name_list(conn, record, suport, connected_list)
			#data received
			else:
				try:
					data_r = sock.recv(buffer)
					data = data_r[:data_r.index("\n")]
					ip,port = sock.getpeername()
					print "Data [ %s ] received from:" % data,"[",record[(ip,port)],"]"

					#data cheking
					if data == "exit":
						exit_chat(sock, record[(ip,port)], record, suport, connected_list)
					elif data == "private":
						private_guide(sock)
					elif "p." in data:
						private_msg(data, sock, suport)
					elif data == "show users":
						show_users(sock, suport, record[(ip,port)])
					else:
						msg = "\r\33[1m"+"\33[35m "+record[(ip,port)]+": "+"\33[0m"+data+"\n"
						send_to_all(sock,msg)
				except:
					(ip,port) = sock.getpeername()
					exit_chat(sock, record[(ip,port)], record, suport, connected_list)
					continue
	server_socket.close()