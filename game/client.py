import socket
import sys

AUTHENTICATING = 0
IN_GAME_HALL = 1

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
                if(message == "1001 Authentication successful\n"):
                    state = IN_GAME_HALL
                    print(message)
                else:
                    print(message)
            
            if state == IN_GAME_HALL:
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
