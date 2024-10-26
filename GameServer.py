
import socket
import random as rd
import threading
import sys
rooms = {1: {"players": [], "condition": threading.Condition()}, 
         2: {"players": [], "condition": threading.Condition()}, 
         3: {"players": [], "condition": threading.Condition()}}
        #for each room create a specific lock for it
room_guess = {1:[], 2:[], 3: []}
room_target = {1:[], 2:[], 3: []}
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
                state = IN_GAME_HALL
                #print(state)
                client_socket.send(b"1001 Authentication successful")
                print("Sent successful Authentication result")
                
            else:
                client_socket.send(b"1002 Authentication failed")
                print("Sent failed Authentication result ")

        if state == IN_GAME_HALL:
            guess_val = None
            print(state)
            try:
                command = client_socket.recv(1024).decode().strip()
            except:
                print(f"user: {threading.get_ident()} is disconnected")
                client_socket.close()
                break #exit loop means the thread comes to the end of execution, thread is dead

            if command == "/list":
                print("Sent list command")
                response = "3001 " + str(len(rooms))
                for i in rooms:
                    response += " "
                    response += str(len(rooms[i]["players"]))
                print(response)
                client_socket.send(response.encode())
            elif command.startswith("/enter"): 
                try:
                    room_number = int(command.split()[1])
                    if room_number in rooms:
                        with rooms[room_number]["condition"]:  # If the lock for this specific room is acquired
                            if len(rooms[room_number]["players"]) < MAX_PLAYERS_PER_ROOM:
                                rooms[room_number]["players"].append(threading.get_ident())  # Record thread ID

                                # If room is still not full after one player added
                                if len(rooms[room_number]["players"]) < MAX_PLAYERS_PER_ROOM:
                                    client_socket.send(b"3011 Wait")
                                    rooms[room_number]["condition"].wait()  # Release the lock and wait
                                    #After wake up
                                    try:
                                        player = client_socket.getsockname()
                                    except:
                                        # if the palyer quit after waiting
                                        rooms[room_number]["players"].remove(threading.get_ident())
                                        print(f"{threading.get_ident()} is disconnected")


                        
                                # If the room is full after one player is added
                                if len(rooms[room_number]["players"]) == MAX_PLAYERS_PER_ROOM:
                                    
                                    # If the targets have not been generated yet
                                    if room_target[room_number] == []:  # Corrected condition check
                                        target = rd.randint(0, 1)  # Generating random boolean value
                                        room_target[room_number] = target
                                    

                                    # Check the guess statement is right or not
                                    Flag = True
                                    while Flag:
                                        client_socket.send(b"3012 Game started. Please guess true or false")
                                        try:
                                            guess = client_socket.recv(1023).decode()
                                            if guess.startswith("/guess"):
                                                try:
                                                    guess = guess.split(" ") # string guess = "/guess 0"
                                                    guess_val = int(guess[1])
                                                    Flag = False
                                                except:
                                                    client_socket.send(b"4002 Unrecognized message.")
                                            else:
                                                client_socket.send(b"4002 Unrecognized message.")
                                        except:
                                            print("User is disconnected")
                                            rooms[room_number]["players"].remove(threading.get_ident())# delete the disconnect user
                                            client_socket.close()
                                            break
                                    if guess_val is None:
                                        break
                                    #guess is valid
                                    else:
                                        room_guess[room_number].append({threading.get_ident(): guess_val})  
                                        state = IN_GAME
                                        rooms[room_number]["condition"].notify_all()  # Wake other players in the same room
                            else:
                                client_socket.send(b"3013 The room is full")
                            
                    else:
                        client_socket.send(b"4003 Room doesn't exist.")  # Added a period for consistency
                            
                except:
                    client_socket.send(b"4002 Unrecognized message.")
                    continue
            elif command == "/Exit":
                    break
                    
            else:
                client_socket.send(b"4002 Unrecognized message.")
                
                

            if state == IN_GAME:
                # check whether user in the room is disconnected

                pass
            #game logics
            # have a varibale room to record the thread key of threading attending this room
            # have a guess varible to record the guess from the thread attending this room
          

    


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
    