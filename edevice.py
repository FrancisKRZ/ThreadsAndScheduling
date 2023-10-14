# Embedded Device:

#     1) Generates random numbers to simulate the device's job time for the compute server.
#     2) Sends the msg (rand num) to the compute server, sleeps for a random number (1-5), before sending again.

#     The msg will look like:     deviceID : job compute time
#                                         3:5

# How it should run:
#     edevice.py <server addr> <server port>

#     * server addr is the Compute Server, server port is the Server's port number.
#     * server port must be a big number lesser than 65,000

# A second embedded device runs like:
#     edevice.py 2 localhost 4017

import sys
import socket
import random as rd
import time
from threading import Lock
from threading import Thread


mutexLock = Lock()
bufferSize = 512
# Embedded Device ID, 1 by default, use Command Line Arguments to Modify
eDev = 1
JobCount = 3
# Keeping track of elapsed time per device
timeElapsed = 0

clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Producer Class:
# Generates random numbers for the Job Compute Time (limited to 10)
# to send to the server
class Producer(Thread):

    def __init__ (self, t_number, server_addr, server_port):

        self.t_number = t_number
        self.server_addr = server_addr
        self.server_port = server_port
        Thread.__init__(self)


    # Define what the Thread(s) do:
    def run(self):
        # print(f"Hello, from Thread #{self.t_number}, {self.server_addr, self.server_port} ")
        addr = (self.server_addr, self.server_port)
        global timeElapsed

        for i in range(JobCount):

            # Random Number Generated capped to 10 for a better experience.
            JobComputeTime = rd.randrange(10)

            mutexLock.acquire()

            # Encodes the message, the eDevice's ID and the JCT
            msg = ( str(eDev) + ":" + str(JobComputeTime) ).encode('ascii')
            
            # Sends the message to the server
            print(f"\n---> Client Sending Data: {msg}")
            clientUDP.sendto(msg, addr)

            mutexLock.release()

            # Receives messages from the server
            data, server = clientUDP.recvfrom(bufferSize)

            # ---- Bonus ----
            # Confirms that we received data, and then sleep for the JCT's duration
            if data:
                print(f"<--- Server Data Received: {data} ")
                recvSleep =  ( (data).decode() ).split(':')[1]
                timeElapsed += int(recvSleep)
                time.sleep( int(recvSleep) )





# Takes two command line arguments, server address and port
def main():

    # Using eDevice's ID
    global eDev
    global timeElapsed

    # Checks if we've an additional command line arg
    # If we have three then it means
    #  we're overwriting the default device's ID from 1
    if len(sys.argv)-1 == 2:
        server_addr = sys.argv[1] 
        server_port = int( sys.argv[2] )

    # Here we overwrite the eDevID from default of 1
    elif len(sys.argv)-1 == 3:
        eDev = sys.argv[1]
        server_addr = sys.argv[2] 
        server_port = int( sys.argv[3] )

    else:
        sys.exit("Incorrect Command-Line Arguments - View READ.ME Instructions...")

    if server_port > 65000:
        sys.exit(f"Invalid Port Number: {server_port} Must be lesser than 65,000")


    # Thread Creations, must be in sync with the Server Side
    idealThreads = 3
    thread = [0] * idealThreads


    # Concept was to send to server how many threads we'll be sending
    # In order it can prepare the correct amount of handlers, instead of hard-coded
    # clientUDP.sendto( (str(jobCount)).encode('ascii'), (server_addr, server_port) )


    # Initiates the threads
    for i in range(idealThreads):
        thread[i] = Producer(i+1, server_addr, server_port)
        thread[i].start()

    # Syncs all threads
    for i in range(idealThreads):
        thread[i].join()

    # Close the client's side UDP
    clientUDP.close()

    # Prints the time spent executing the threads.
    print(f"Time Elapsed: {timeElapsed} seconds.")



if __name__ == "__main__":
    main()