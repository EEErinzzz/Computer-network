#!/usr/bin/python3
import os.path
import socket
import sys

def main(argv):
    # get port number from argv
    serverport = int(argv[1])

    # create socket and bind
    try:
        sockfd = socket.socket()
            #When you call socket.socket() without any arguments, by default, it creates TCP socket
        sockfd.bind(('',serverport ))
        sockfd.listen(5)
        print("The server is ready to receive")
    except socket.error as  emsg:
        print("Socket bind error:", emsg)
        sys.exit(1)
    

    # accept new connection
    while True:       
        try:
            conn, addr = sockfd.accept() # addr is the address of the client
        except socket.error as acptmsg:
            print("socket accept error", acptmsg)
            sys.exit(1)
        print("Connection established. Here is the remote peer info:", addr)
        
        # receive file name/size message from client 
        try:
            fileinfo= conn.recv(1024).decode('ascii')
        except socket.error as recverror:
            print("file infor receive error", recverror)
            sys.exit(1)

        #use Python string split function to retrieve file name and file size from the received message
        fname, filesize = fileinfo.split(":")
        print("Open a file with name \'%s\' with size %s bytes" % (fname, filesize))
        
        #create a new file with fname
        try:
            fd = open(fname, "wb") # write binary
        except os.error as flerror:
            print("File open error", flerror)
            sys.exit(1)
       
       # send OK to the client that the server is ok for receiving files
        remaining = int(filesize)
        conn.send(b"OK")
        print("Start receiving . . .")

        while remaining > 0:
            # receive the file content into rmsg and write into the file
            try:
                rmsg = conn.recv(1000)
            except socket.error as recvmsg:
                print("File content receive error:", recvmsg)
                sys.exit(1)
            try:
                fd.write(rmsg)
                remaining -= len(rmsg)
            except os.error as wrterror:
                print("file write error:", wrterror)
            
        print("[Completed]")
        fd.close()
        conn.close()
    sockfd.close()
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 FTServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)