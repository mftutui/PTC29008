import socket, select, string, sys

def display():
	you = "\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def private_message(user,msg):
    print "Private message for you!"
    msg = "\33[34m\33[ "+ user+": \33[0m"+msg
    sys.stdout.write(msg)  
    sys.stdout.flush()

def name_empty():
    name = raw_input("\33[34m\33[1mEnter username: \33[0m")
    while (name is None) or (str(name).strip() == ""):
	    print ("\33[31m\33[1mUsername is empty!\33[0m")
            name = raw_input("\33[34m\33[1mEnter username: \33[0m")
    return name

def main():
    host = "localhost"
    port = 5003

    name = name_empty()
    
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
                    print '\33[31m\33[1m \rYOU ARE DISCONNECTED!!\n \33[0m'
                    sys.exit()
                elif "private" in data:
                    name_p = data[data.find(";"):data.find(":")]
                    print name_p
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

    # se eu mandar uma mensagem para privada para um usuario que n existe