
import socket
# from telnetlib import AUTHENTICATION
import threading
import sys

rooms = {1: [], 2: [], 3: []}  # Example: 1:{10, 11} thread 10 and thread 11 are in room1
# State varible
AUTHENTICATING = 0
IN_GAME_HALL = 1
MAX_PLAYERS_PER_ROOM = 2
IN_GAME = 3
EXIT = 4

def load_user_info(USER_INFO_PATH):
    # return a dictionary of UserInfo.txt to record the key of corresponding user
    # the return data type is dictionary that can be shared by threads
    user_info = {}
    with open(USER_INFO_PATH, 'r') as file:
        for line in file:
            username, password = line.strip().split(':')
            user_info[username] = password
    print(user_info)
    return user_info 


def handle_client(client_socket, user_info): 
    #client_socket: sockect connecting to the specific client from the server
    # user_info: ictionary recording name and key of users
    state = AUTHENTICATING
    while True:
        if state == AUTHENTICATING:
            client_socket.send(b"Please input your user name:")
            username = client_socket.recv(1024).decode()
            print("reveived name:", username)
            client_socket.send(b"Plese input your password:")
            key = client_socket.recv(1024).decode()
            print("reveived key:", key)
            if username in user_info and user_info[username] == key:
                client_socket.send(b"1001 Authentication successful")
                print("Sent successful Authentication result ")
                state = IN_GAME_HALL
            else:
                client_socket.send(b"1002 Authentication failed")
                print("Sent failed Authentication result ")

        if state == IN_GAME_HALL:
            # Game hall logic
            ...
            #change state to game if possible
            pass
        if state == IN_GAME:
            #game logic
            # have a varibale room to record the thread key of threading attending this room
            # have a guess varible to record the guess from the thread attending this room
            pass
        if state == EXIT:
            
            break

    client_socket.close()



def start_server(server_port, user_info): 
    #receive designated server port NO.

    # Create a main socket and bind
    try:
        sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockfd.bind(('', server_port))
        sockfd.listen(5)
        print("The server is ready to receive")
    except socket.error as emsg:
        print("Socket bind error:", emsg)
        sys.exit(1)

    #Try to accept new user by subsockect
    while True:
        try:
            conn, addr = sockfd.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(conn, user_info))# cnn is the socket id used to accept new user
            client_thread.start()
        except socket.error as acptmsg: #If sockect is used up and no more user can enter
            print("Socket accept error", acptmsg)
            sockfd.close()
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
    #The server program takes 2 parameters:(required by the homework)
    #(1) server’s listening port; (2) path to a UserInfo.txt file
        print("Usage: python3 GameServer.py <Server_port> <path to a UserInfo.txt file>")
        sys.exit(1)
    user_info = load_user_info(sys.argv[2])
    start_server(int(sys.argv[1]), user_info)
    
