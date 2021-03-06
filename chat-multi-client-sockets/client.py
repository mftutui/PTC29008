# https://github.com/mftutui/PTC29008

import socket, select, string, sys

def display():
	you = "\33[33m\33[1m"+"You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def check_name_empty():
    name = raw_input("\33[34m\33[1mEnter username: \33[0m")
    while (name is None) or (str(name).strip() == ""):
	    print ("\33[31m\33[1mUsername is empty!\33[0m")
            name = raw_input("\33[34m\33[1mEnter username: \33[0m")
    return name

def exit_chat(client_socket):
    client_socket.close()

def main():
    port = 5001
    name = check_name_empty()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)

    try :
        client_socket.connect(("localhost", port))
    except :
        print "\33[31m\33[1m Can't connect to the server.\33[0m"
        sys.exit()

    client_socket.send(name)
    display()

    while 1:
        socket_list = [sys.stdin, client_socket]
        rList, wList, error = select.select(socket_list , [], [])

        for sock in rList:
            #incoming message from server
            if sock == client_socket:
                data = sock.recv(4096)
                if not data :
                    print '\33[31m\33[1m \rYOU ARE DISCONNECTED!!\n \33[0m'
                    sys.exit()
                elif data == "exit_chat":
                    exit_chat(client_socket)
                else:
                    sys.stdout.write(data)
                    display()
            else:
                msg = sys.stdin.readline()
                client_socket.send(msg)
                display()

if __name__ == "__main__":
    main()