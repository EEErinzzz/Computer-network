from socket import *
import sys

setdefaulttimeout(15)

def main(args):
    server_address = args[1]
    listen_port = args[2]
    
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, int(listen_port)))
    except timeout as emsg:
        print("Connection timeout! Please enter a correct Hostname or IP address. Error message: ", emsg)
        sys.exit(1)
    except error as emsg:
            print("Socket error: ", emsg)
            sys.exit(1)
    except KeyboardInterrupt:
            print("You terminate this process")
            sys.exit(1)
    
    while True:
        username = input("Please input your user name: ")
        pwd = input("Please input your password: ")

        auth_msg = f"/login {username} {pwd}"
        client_socket.send(auth_msg.encode())

        #print("From server:", client_socket.recv(50)) # For checking
        login_reply = client_socket.recv(50).decode() # Result of login         

        if login_reply.split(" ")[0] == "1001":
            print(login_reply)
            break
        else:
             print(login_reply)
    
    ingame = False

    while True:
        msg_to_server = input()
        client_socket.send(msg_to_server.encode())

        server_msg = client_socket.recv(50).decode()
        print(server_msg)
        if server_msg.split(" ")[0] == "4001":
            client_socket.close()
            sys.exit(1)
             
             



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <Host_name> <Listen_port>")
        sys.exit(1)
    main(sys.argv)