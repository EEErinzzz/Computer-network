import socket
import random as rd
import threading
import sys
import time

rooms = {1: [], 
         2: [], 
         3: []}
        #for each room create a specific lock for it
rooms_guess_answer = {1: None, 2: None, 3: None}
rooms_player_guess = {1: [None, None], 2: [None, None], 3: [None, None]}
rooms_connection_status = {1: [True, True], 2: [True, True], 3: [True, True]}
lock = threading.Lock()


# State varible
AUTHENTICATING = 0
IN_GAME_HALL = 1
MAX_PLAYERS_PER_ROOM = 2
IN_GAME = 3
EXIT = 4

def get_thread_by_id(thread_id):
    for thread in threading.enumerate():
        if thread.ident == thread_id:
            return thread
    return None


def check_thraed_alive(room_number):
    # Check if the thread is still alive
    for id in rooms[room_number]:
        try:
            if threading.Thread.is_alive(get_thread_by_id(id)) == False:
                return id
        except AttributeError:
            return id
    return 0


def rooms_generate_guess(room_number):
    # Provided that the room_number is correct
    randint = rd.randint(1,10)
    if randint >= 5:
        rooms_guess_answer[room_number] = "true"
    else:
        rooms_guess_answer[room_number] = "false"
    print("Server log: Gen result:", rooms_guess_answer[room_number])

def reset_room(room_number):
    rooms[room_number] = []
    rooms_guess_answer[room_number] = None
    rooms_player_guess[room_number] = [None, None]
    rooms_connection_status[room_number] = [True, True]


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
    room_number = 0
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
                    response += str(len(rooms[i]))
                print(rooms, rooms_guess_answer, rooms_player_guess, rooms_connection_status)
                client_socket.send(response.encode())
            elif command.startswith("/enter"): 
                try:
                    room_number = int(command.split(" ")[1])
                    # Must check room_number here
                    if len(rooms[room_number]) >= 2:
                        client_socket.send(b"Room full")
                        continue
                except IndexError:
                    client_socket.send(b"Please enter a room number")
                    continue
                state = IN_GAME
                
            elif command == "/exit":
                    print(f"Server log: {threading.get_ident()} exit command detected. Connection eneded")
                    client_socket.send(b"4001 Bye bye")
                    client_socket.close()
                    return
                    
            else:
                client_socket.send(b"4002 Unrecognized message.")
                
                

            if state == IN_GAME:
                # check whether user in the room is disconnected
                # After the player receiving the "3012" msg
                lock.acquire()
                # Update the rooms dictionary: Add this thread to corresponding room
                rooms[room_number].append(threading.get_ident()) # room_number should be prepared by the previous state (Not error detection)
                player_index = rooms[room_number].index(threading.get_ident())
                lock.release()
                ## 3011 Wait case
                if len(rooms[room_number]) < 2:
                    client_socket.send(b"3011 Wait")
                    while True:
                        time.sleep(1)
                        print(len(rooms[room_number]))
                        client_socket.send(b"5001 SYN") #Send 5001 SYN msg to the client to check if the client is still online
                        
                        #Client should return SYN ACK msg

                        try:
                            client_msg = client_socket.recv(50)
                            # Verify the msg if needed
                        except TimeoutError:
                            print(f"Server log: {threading.get_ident()} haven't respond for a long time. Connection terminated" )
                            lock.acquire()
                            rooms[room_number].remove(threading.get_ident())
                            lock.release()
                            return
                        except ConnectionAbortedError:
                            print(f"Server log: {threading.get_ident()} terminated this connection. Connection ended")
                            lock.acquire()
                            rooms[room_number].remove(threading.get_ident())
                            lock.release()
                            return
                            ## More exception if needed
                        if len(rooms[room_number]) == 2:
                            print("Break")
                            break

                ## 3012 Game Started case

                ## Double check if the client is still in the room (online)
                checking = check_thraed_alive(room_number)
                if check_thraed_alive(room_number) != 0:
                    print("Sever log: A client is offline while joining the room, removing the client from the room")
                    lock.acquire()
                    rooms[room_number].remove(checking)
                    lock.release()

                rooms_generate_guess(room_number)
                client_socket.send(b"3012 Game Started. Please guess true or false")
                answer_guess = rooms_guess_answer[room_number]
                while True and state == IN_GAME:
                    
                    # Step 1: Get Guess from client
                    try:
                        client_msg = client_socket.recv(50).decode()
                    except ConnectionAbortedError:
                        print(f"Server log: {threading.get_ident()} terminated this connection. Connection ended")
                        if threading.get_ident() in rooms[room_number]:
                                    rooms[room_number].remove(threading.get_ident())
                        rooms_connection_status[room_number][player_index] = False
                        return
                    except TimeoutError:
                        print(f"Server log: {threading.get_ident()} haven't respond for a long time. Connection terminated" )
                        if threading.get_ident() in rooms[room_number]:
                            rooms[room_number].remove(threading.get_ident())
                        rooms_connection_status[room_number][player_index] = False
                        return
                    # Step 2: Check if the guess has correct format
                    if client_msg.split(" ")[0] == "/guess":
                        try:
                            client_guess = client_msg.split(" ")[1]
                        except IndexError:
                            client_socket.send(b"4002 Unrecognized message")
                            continue
                        if client_guess != "true" and client_guess != "false": ## Seems that the value of guess should either be "true" or "false" (Not True and False) in the sample testcase
                            client_socket.send(b"4002 Unrecognized message")
                            continue
                        # Step 3: Update client's guess to the server storage
                        lock.acquire()
                        rooms_player_guess[room_number][player_index] = client_guess
                        lock.release()
                        # Step 4: Wait for the other client
                        while True:
                            ## Compare client_guess with another client's

                            # Step 5: If both of them made guesses
                            if rooms_player_guess[room_number][0] != None and rooms_player_guess[room_number][1] != None:
                                #Tie
                                if rooms_player_guess[room_number][0] == rooms_player_guess[room_number][1]:
                                    print("Send 3023")
                                    client_socket.send(b"3023 The result is a tie")
                                    if len(rooms[room_number]) == 1:
                                        reset_room(room_number)
                                    state = IN_GAME_HALL
                                    break
                                #Win
                                print("Server log: ", client_guess, rooms_guess_answer[room_number])
                                if client_guess == rooms_guess_answer[room_number]:
                                    client_socket.send(b"3021 You are the winner")
                                    if len(rooms[room_number]) == 1:
                                        reset_room(room_number)
                                    state = IN_GAME_HALL
                                    break
                                #Lose
                                else:
                                    print("???", client_guess, rooms_guess_answer[room_number])
                                    client_socket.send(b"3022 You lost this game")
                                    if rooms[room_number] == 1:
                                        reset_room(room_number)
                                    state = IN_GAME_HALL
                                    break
                            #Step 4a: Waiting for the other player
                            if len(rooms[room_number]) == 2:
                                # SYN1: Send SYN msg to the client
                                client_socket.send(b"5001 SYN")
                            else:
                                # Step 4b: The other client left, game over now
                                if rooms_connection_status[room_number][1 - player_index] == False:
                                    client_socket.send(b"3021 You are the winner")
                                    reset_room(room_number)
                                    state = IN_GAME_HALL
                                    break

                            try:
                                # SYN1: Check SYN msg to the client
                                msg = client_socket.recv(50)
                            # # SYN1: Failed, this client is offline -> remove this client from the room list
                            except TimeoutError:
                                print(f"Server log: {threading.get_ident()} haven't respond for a long time. Connection terminated" )
                                lock.acquire()
                                rooms[room_number].remove(threading.get_ident())
                                if len(rooms[room_number]) == 0:
                                    reset_room(room_number)
                                lock.release()
                                return
                            except ConnectionAbortedError:
                                print(f"Server log: {threading.get_ident()} terminated this connection. Connection ended")
                                lock.acquire()
                                if threading.get_ident() in rooms[room_number]:
                                    rooms[room_number].remove(threading.get_ident())
                                if len(rooms[room_number]) == 0:
                                    reset_room(room_number)
                                lock.release()
                                return
                            except Exception as e:
                                print(f"Server log: {threading.get_ident()} terminated this connection. Connection ended", e)
                                lock.acquire()
                                if threading.get_ident() in rooms[room_number]:
                                    rooms[room_number].remove(threading.get_ident())
                                if len(rooms[room_number]) == 0:
                                    reset_room(room_number)
                                lock.release()
                            ## More exception if needed

                            # When the other player left
                            if len(rooms[room_number]) == 1 and rooms_connection_status[room_number][1 - player_index] == False:
                                client_socket.send(b"3021 You are the winner")
                                reset_room(room_number)
                                state = IN_GAME_HALL
                                break
                    else:
                        client_socket.send(b"4002 Unrecognized message")
                if threading.get_ident() in rooms[room_number]:
                    lock.acquire()
                    rooms[room_number].remove(threading.get_ident())
                    reset_room(room_number)
                    lock.release()
                    

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
    