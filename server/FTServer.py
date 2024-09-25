#!/usr/bin/python3

import socket
import sys

def main(argv):
    # get port number from argv
    
   
    # create socket and bind
    
    
    
    
    
    
    
    sockfd.listen(5)
    
    print("The server is ready to receive")
    
    while True:
        
        # accept new connection
        
        
        
        
        
        
        # receive file name/size message from client 
        
        
        
        
        
            
        
        
        #use Python string split function to retrieve file name and file size from the received message
        fname, filesize = 
        
        print("Open a file with name \'%s\' with size %s bytes" % (fname, filesize))
        
        #create a new file with fname
       
       
       
       
       
        
        remaining = int(filesize)

        conn.send(b"OK")

        print("Start receiving . . .")
        while remaining > 0:
            # receive the file content into rmsg and write into the file
            
            
            
            
            remaining -= len(rmsg)

        print("[Completed]")
        fd.close()
        conn.close()
        
    sockfd.close()
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 FTServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)