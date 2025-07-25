from errno import ENFILE
import socket
import threading
import subprocess
from fastcore.basics import listify
from time import sleep

HEADER_SIZE = 16
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 4242
TIMEOUT = 600
FORMAT = 'utf-8'
DISCONNECT_MSG = bytes(f"{10:<{HEADER_SIZE}}", 'utf-8') + b'DISCONNECT'
END_OF_MESSAGE = ''
CLI = 'hackrf_sweep'

def parse_command(message):
    cmds = []
    for c in message.split():
        cmd = c.split('=') if '=' in c else c
        cmds.extend(listify(cmd))
    return cmds

def process_message(message):
    command = parse_command(message)
    print(command)
    sweep = subprocess.run([CLI] + command, stdout=subprocess.PIPE)
    yield from sweep.stdout.splitlines()

def encode_msg(msg):
    message = msg.encode(FORMAT)
    return bytes(f"{len(message):<{HEADER_SIZE}}", 'utf-8') + message


def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')
    try:
        while True: # wait to receive information from the client
            if msg_length := conn.recv(HEADER_SIZE).decode(FORMAT):
                msg_length = int(msg_length)
                if not msg_length: break
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == "DISCONNECT": break
                print(f'[{addr}] {msg}')
                for response in process_message(msg):
                    response = bytes(f"{len(response):<{HEADER_SIZE}}", 'utf-8') + response
                    conn.send(response)
                conn.send(encode_msg(END_OF_MESSAGE))
    finally:
        print(f"[DISCONNECTED] {addr} disconnected")
        conn.close()


def main(server: str = SERVER, # Server IP to listen and receive connection
         port: int = PORT, # Port to listen on Server IP
):
    print("[STARTING]Server is starting...")

    # Create a socket
    # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
    # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_ - socket option
    # SOL_ - socket option level
    # Sets REUSEADDR (as a socket option) to 1 on socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind, so server informs operating system that it's going to use given IP and port
    # For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
    server_socket.bind((server, port))
    # This makes server listen to new connections
    server_socket.listen()
    print(f'[LISTENING] Server is listening on IP {server} PORT {port}')

    timeout = 300
    try:
        while True:
            # now our endpoint knows about the OTHER endpoint.
            clientsocket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(clientsocket, address))
            thread.start()
            connections = threading.active_count() - 1
            if not connections:
                if not timeout: break
                sleep(1)
                timeout -= 1
            else:
                timeout = TIMEOUT
            print(f'[ACTIVE CONNECTIONS] {connections}')
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()



# print(f'Sweep efetuado com sucesso: {sweep.returncode}')
# for line in sweep.stdout.splitlines():
#     clientsocket.send(line)
#     sleep(1)
# server_socket.close()





