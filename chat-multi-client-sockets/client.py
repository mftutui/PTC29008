import socket, select, string, sys

def display():
	you = "\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def private_message(user,msg):
    sys.stdout.write("\33[34m\33["+user+": \33[0m"+msg)  
    sys.stdout.flush()

def main():
    host = "localhost"
    port = 5001
    name = ""

    name = raw_input("\33[34m\33[1m Enter username: \33[0m")

    while (name is None) or (str(name).strip() == ""):
	    print ("\r\33[31m\33[1m Username is empty \n\33[0m")
            name = raw_input("\33[34m\33[1m Enter username: \33[0m")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)
        
    try :
        client_socket.connect((host, port))
    except :
        print "\33[31m\33[1m Can't connect to the server \33[0m"
        sys.exit()

    client_socket.send(name)
    display()

    while 1:
        socket_list = [sys.stdin, client_socket]
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            #incoming message from server
            if sock == client_socket:
                data = sock.recv(4096)
                if not data :
                    print '\33[31m\33[1m \r YOU ARE DISCONNECTED!!\n \33[0m'
                    sys.exit()
                elif "private" in data:
                    name_p = data[data.find(";"):data.find(":")]
                    msg = data[data.find(":")+1:]
                    private_message(name_p,msg)
                else:
                    sys.stdout.write(data)
                    display()
            else:
                msg = sys.stdin.readline()
                client_socket.send(msg)
                display()

if __name__ == "__main__":
    main()