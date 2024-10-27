import socket
import sys

AUTHENTICATING = 0
IN_GAME_HALL = 1
IN_GAME = 2

def wait(sf):
    while True: 
        sf.send("SYN".encode())
        msg = sf.recv(50).decode()
        if msg.split(" ")[0] == "5001":
             continue
        else:
            print(msg)
            return


def main(server_ip, server_port):
    state = AUTHENTICATING
    """Main function to connect to the server and interact with it."""
    try:
        # Create a socket to connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_socket.settimeout(15) # Default timeeout is 15 seconds
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
                client_socket.settimeout(30)
                command = input("Enter a command: ")  # Added prompt for clarity
                client_socket.send(command.encode()) 
                try:
                    response = client_socket.recv(1024).decode()
                    print(response)
                    
                    #Start with 30XX
                    if response.startswith("30"):
                        if response.startswith("3011"):  # Handle wait message
                            print("Waiting for another player...")
                            while True:
                                server_msg = client_socket.recv(50).decode()
                                if server_msg.startswith("5001"):
                                    client_socket.send(b"SYN ACK")
                                if server_msg.split(" ")[0] == "3012":
                                    print(server_msg)
                                    break

                        
                    elif response.startswith("40"):
                        if response.startswith("4001"):
                            client_socket.close()
                            sys.exit(1)  
                            return
                        continue  # Handle error messages starting with "40"
                    elif response.startswith("5001"):
                        wait(client_socket)

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