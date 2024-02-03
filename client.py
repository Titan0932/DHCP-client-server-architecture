import socket
import time
import os
from pathlib import Path
from dotenv import load_dotenv
import threading


# dotenv_path = Path('/.env')
load_dotenv()
PORT = int(os.getenv('PORT'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), PORT))


def printServerMsg(msg):
    print("\n|-------------------- SERVER SAYS --------------------|\n")
    print("         ", msg.decode('utf-8'))
    print("\n|-------------------- ====== ==== --------------------|\n")


def clientAction():
    msg = s.recv(1024)
    printServerMsg(msg)
    while True:
        print("\n|============= MENU: ==========|\n")
        print("'ASK' To Generate IP_ADDRESS\n")
        print("'RENEW' IP_ADDRESS\n")
        print("'RELEASE'  IP_ADDRESS\n")
        print("'STATUS'  IP_ADDRESS\n")
        print("|=========================|")
        try:
            command = input("\nEnter a command: ")
        except:
            print("\nEXITING.........")
            exit(0)

        s.send(bytes(command, 'utf-8'))
        msg = s.recv(1024)
        printServerMsg(msg)
        time.sleep(1)

def main():
    clientAction_thread = threading.Thread(target=clientAction)
    clientAction_thread.start()
    

if __name__ == "__main__":
    main()