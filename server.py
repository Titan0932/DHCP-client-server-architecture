import socket
import time
import threading
import os
import sys

from dotenv import load_dotenv
from pathlib import Path

# dotenv_path = Path('.')
load_dotenv()


IP_LIMIT = int(os.getenv('IP_LIMIT'))

TIME_OUT = int(os.getenv('TIME_OUT'))

HOST_IP = os.getenv('HOST_IP')

PORT = int(os.getenv('PORT'))

SERVER_ERROR = os.getenv('SERVER_ERROR')

mainServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainServer.bind((socket.gethostname(), PORT))

lock = threading.Lock()

EXIT = False

ip_dict = {HOST_IP : [False, None],
           '0.0.0.1': [True, '111231.1']} # [is_avaiable, time, is_active, MAC_ADDRESS] | Note: we did not implement the other aspects like checking device mac for simplicity


def ask():
    with lock:
        dict_len = len(ip_dict)
        for i in range(dict_len):
            ip = list(ip_dict.keys())
            # print(ip[i])
            if ip_dict[ip[i]][0] == True:
                print(f"Offer {ip[i]}")
                ip_dict[ip[i]] = [False, time.time()]
                return ip[i]
        ip = list(ip_dict)[-1].split(".")
        # print("Last: ", ip)
        for i in range(3, -1, -1):
            if int(ip[i]) < IP_LIMIT:
                ip[i] = str(int(ip[i])+1)
                break
            else:
                ip[i] = "0"
        ip = ".".join(ip)
        ip_dict.update({ip: [False, time.time()]})
        print(f"Offer {ip}")
        return ip
            
def renew(userIP):
    with lock:
        if(userIP not in ip_dict.keys() or ip_dict[userIP][0] == False):
            print(SERVER_ERROR + " ERROR" + ": INVALID REQUEST")
            return(SERVER_ERROR + " ERROR" + ": INVALID REQUEST")
        else:
            # check if device is correct LATER
            ip_dict[userIP][1] = time.strftime("%H:%M:%S")

def release(userIP):
    with lock:
        if(userIP not in ip_dict.keys() or ip_dict[userIP][0] == True):
            print(SERVER_ERROR + " ERROR" + ": INVALID REQUEST")
            return(SERVER_ERROR + " ERROR" + ": INVALID REQUEST")
        else:
            ip_dict[userIP] = [True, '']
            return "RELEASED " + str(userIP)

        
def status(userIP):
    with lock:
        if(userIP not in ip_dict.keys() or ip_dict[userIP][0] == True):
            print(userIP + " AVAILABLE")
            return userIP + " AVAILABLE"
        else:
            print(userIP + " ASSIGNED")
            return userIP + " ASSIGNED"


def net_comms(command, conn, userIP = ""):
    match command:
        case "ASK":
            print(f"\nClient at address f{conn.getpeername()}: REQUESTING IP ADDRESS! ")
            conn.send(ask().encode("utf-8"))
        case "RENEW":
            print(f"\nClient at address f{conn.getpeername()}: RENEWING IP ADDRESS {userIP}! ")
            conn.send(renew(userIP).encode("utf-8"))
        case "RELEASE":
            print(f"\nClient at address f{conn.getpeername()}: RELEASING IP ADDRESS {userIP}! ")
            conn.send(release(userIP).encode("utf-8"))
        case "STATUS":
            print(f"\nClient at address f{conn.getpeername()}: REQUESTING STATUS of IP ADDRESS {userIP}! ")
            conn.send(status(userIP).encode("utf-8"))
        case _:
            print(f"\nClient at address f{conn.getpeername()}: Using command: {command} ")
            conn.send(bytes("INVALID REQUEST", "utf-8"))

def time_out():
    with lock:
        for ip in ip_dict:
            if ip != HOST_IP:
                if ip_dict[ip][0] == False:
                    print(time.time())
                    print (time.time() - float(ip_dict[ip][1]))
                    if time.time() - float(ip_dict[ip][1]) > TIME_OUT:
                        print("RELEASING IP: ", ip)
                        ip_dict[ip] = [True, ""]

def getClientResponse(conn, curTime):
    global EXIT
    while not EXIT:
        try:
            data = conn.recv(1024)
        except ConnectionAbortedError:
            print("Connection was aborted: ", conn)
            break
        except socket.timeout:
            continue
        data = data.decode("utf-8").split(" ")
        if len(data) > 0:
            checkIP = data[1] if len(data) > 1 else "" 
            net_comms(data[0].upper(), conn, checkIP)
            
def getConnection():
    global EXIT
    while not EXIT:
        try:
            conn, address = mainServer.accept()
        except socket.timeout:
            continue
        if conn:
            print("CONNECTION INITIALIZED!! \n")
            print(f"Connected by {address}")
            conn.send(("Welcome to the server!").encode("utf-8"))
            # connections.append([conn, address, time.time()])
            getClientResponse_thread = threading.Thread(target=getClientResponse, args=(conn, time.time()))
            getClientResponse_thread.start()

def checkTimeOut():
    global EXIT
    curTime = time.time()
    while not EXIT:
        if time.time() - curTime >= TIME_OUT:
            time_out()
            curTime = time.time()

def main():
    global EXIT
    mainServer.settimeout(1)
    mainServer.listen()
    try:
        connectionReqs_thread = threading.Thread(target=getConnection)
        connectionReqs_thread.start()
        checkTimeOut_thread = threading.Thread(target=checkTimeOut)
        checkTimeOut_thread.start()
        while True:  # keep the main thread running indefinitely
            time.sleep(1)  # sleep for a short time to reduce CPU usage
    except KeyboardInterrupt:
        print("CTRL + C Detected! EXITING SERVER!!!")
        EXIT = True
    except Exception as error:
        print("ERROR:" , error)

      

if __name__ == "__main__":
    main()

# def serverWork():
#         # print("CONNECTIONS: ", connections, "\n")
#         for connection in connections:
#             conn, address, curTime = connection[0], connection[1], connection[2]
#             with conn:
#                 getClientResponse_thread = threading.Thread(target=getClientResponse, args=(conn, curTime))
#                 getClientResponse_thread.start()

  