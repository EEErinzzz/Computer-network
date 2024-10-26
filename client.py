import socket
import sys

AUTHENTICATING = 0
IN_GAME_HALL = 1
IN_GAME = 2

def main(server_ip, server_port):
    state = AUTHENTICATING
    """Main function to connect to the server and interact with it."""
    try:
        # Create a socket to connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print("Connected to the server.")

        while True:
            if state == AUTHENTICATING:
            # Receive ask for name message
                message = client_socket.recv(1024).decode()
                print(message)
                username = input()
            # Get user name and send it to the server
                client_socket.send(username.encode())
            #Receive ask for key message
                message = client_socket.recv(1024).decode()
                print(message)
                userkey = input()
                client_socket.send(userkey.encode())
            #Receive authenticating result message
                message = client_socket.recv(1024).decode()
                print(message)
                if(message == "1001 Authentication successful"):
                    state = IN_GAME_HALL
            
            if state == IN_GAME_HALL:
                command = input("Enter a command: ")  # Added prompt for clarity
                client_socket.send(command.encode()) 
                try:
                    response = client_socket.recv(1024).decode()
                    print(response)
                    if response.startswith("30"):
                        
                        if response.startswith("3012"):  # if guess is requested
                            flag = True  # Initialize flag for guessing loop
                            while flag:  # Loop to get valid guess
                                guess = input("Make a guess (true/false): ")  # Added prompt for clarity
                                client_socket.send(guess.encode())
                                guess_parts = guess.split(" ")

                                if len(guess_parts) == 2 and guess_parts[0] == "/guess" and (guess_parts[1] == "false" or guess_parts[1] == "true"):
                                    state = IN_GAME
                                    flag = False
                                else:
                                    print("Invalid guess format. Use '/guess true' or '/guess false'.")

                        elif response.startswith("3011"):  # Handle wait message
                            print("Waiting for another player...")
                        
                    elif response.startswith("40"):
                        continue  # Handle error messages starting with "40"

                except Exception as e:  # Catch any exceptions and print the error
                    print("Server is disconnected:", e)
    
            if state == IN_GAME:
                pass
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 GameClient.py <Server_IP> <Server_Port>")
        sys.exit(1)

    server_ip = sys.argv[1]  # Server IP address
    server_port = int(sys.argv[2])  # Server port number
    main(server_ip, server_port)