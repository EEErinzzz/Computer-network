# To-Do
# Add thread lock
# Add Gameplay logic
# Complete the /enter command

from socket import *
import sys
import os.path
import threading

room_list = []
player_list = []
userinfo = {}

class Room():
    def __init__(self, index):
        self.capacity = 6 # Max capactiy per room
        self.players = [] # The list contains players that are inside this room
        self.index = index



class ServerThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
    def run(self):
        current_state = "Out of house" # The current state of this client
        connectionSocket, addr = self.client
        print("Sever log: New connection established:", connectionSocket)
        connectionSocket.settimeout(15) # Default timeout : 15 seconds
        
        while True:
            try:
                client_msg = connectionSocket.recv(1024) # For communication between the client and server
            except timeout:
                    print(f"System log: {connectionSocket} Process ended: The client haven't respond for a long time")
                    connectionSocket.close()
                    return
            except ConnectionAbortedError:
                    print(f"System log: {connectionSocket} Process eneded: The client ended communication")
                    connectionSocket.close()
                    return
            decoded_client_msg = client_msg.decode()
            #/login command
            if decoded_client_msg.split(" ")[0] == "/login" :
                if userinfo.get(decoded_client_msg.split(" ")[1]) != None :
                    if decoded_client_msg.split(" ")[2] == userinfo[decoded_client_msg.split(" ")[1]]:
                        connectionSocket.send(f"1001 Authentication successful".encode())
                        current_state = "In hall"
                        print(f"Server log: {decoded_client_msg.split(" ")[1]} login successfully")
                        player_list.append(decoded_client_msg.split(" ")[1])
                        print(player_list)
                    else:
                        connectionSocket.send(f"1002 Authentication failed".encode())
                        print(f"Server log: {decoded_client_msg.split(" ")[1]} login failed: Incorrect password")
                else:
                    print(f"Server log: {decoded_client_msg.split(" ")[1]} not found")
                    connectionSocket.send(f"1002 Authentication failed".encode())
            
            # /list command
            elif decoded_client_msg.split(" ")[0] == "/list" :
                print("Server log: Generating room summary")
                re = report(room_list)
                connectionSocket.send(f"3001 {re}".encode())

            # /enter command
            elif decoded_client_msg.split(" ")[0] == "/enter" :
                room_number = int(decoded_client_msg.split(" ")[1]) - 1
                try:
                    #check room condition
                    if room_number == -1: # Python treats Array[-1] as correct syntax
                        connectionSocket.send("Invalid room number".encode())
                    elif len(room_list[room_number].players) < room_list[room_number].capacity:
                        connectionSocket.send("3011 Wait".encode())
                    else:
                        connectionSocket.send("Room full".encode())
                except IndexError:
                    connectionSocket.send("Invalid room number".encode())
            
            # /exit command
            elif decoded_client_msg.split(" ")[0] == "/exit" :
                connectionSocket.send("4001 Bye bye".encode())
                connectionSocket.close()
                return
            else:
                connectionSocket.send("4002 Unrecognized message".encode())

class ServerMain:
    def init_run(self, args):

        #Create rooms
        no_of_rooms = 10
        for i in range(no_of_rooms): 
            room = Room(i)
            room_list.append(room)



        listenPort = args[1]
        serverAddress = "" # In case the value changed
        welcome_socket = socket()
        welcome_socket.bind((serverAddress, int(listenPort)))
        welcome_socket.listen(20)
        
        path = args[2] # Path to the UserInfo.txt

        try:
            with open(path) as f:
                for record in f:
                    (username, password) = record.split(":")
                    userinfo[username] = password.strip("\n")
        except os.error as emsg:
            print("Can't open targeted file: ", emsg)
            sys.exit(1)
        print("Server log: This server is now ready")
        print("UserInfo:", userinfo)
        print("Rooms report:", report(room_list))
        while True:
            client = welcome_socket.accept()
            t = ServerThread(client)
            t.start()

#rooms is a list of room
def report(rooms):
    return_list = []
    num_of_rooms = 0
    for room in rooms:
        return_list.append(len(room.players))
        num_of_rooms += 1
    return f"{num_of_rooms} {return_list}".translate({ord('['):None, ord(']'):None, ord(','):None})



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <Server_port> <Path_to_UserInfo.txt")
        sys.exit(1)
    server = ServerMain()
    server.init_run(sys.argv) #Start the server