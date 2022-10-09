import socket
import json
from typing import Optional

HEADER_SIZE = 16
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 4242
FORMAT = 'utf-8'
DISCONNECT_MSG = 'DISCONNECT'
# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((SERVER, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

def encode_msg(msg):
    message = msg.encode(FORMAT)
    return bytes(f"{len(message):<{HEADER_SIZE}}", 'utf-8') + message


def send(msg):
    client_socket.send(encode_msg(msg))
    while msg_length := client_socket.recv(HEADER_SIZE).decode(FORMAT):
        msg_length = int(msg_length)
        if not msg_length: break
        msg = client_socket.recv(msg_length).decode(FORMAT)
        print(msg)
        if msg == 'DISCONNECT': break

def fix_limits(value, min_val, max_val):
    if value < min_val: 
        return min_val
    return max_val if value > max_val else value

def sweep(serial_number: Optional[str] = None, # -d: Serial number of desired HackRF
          amp_enable: bool = False, # -a: RX RF amplifier True=Enable, False=Disable
          freq_min: int = 1, # -f: Minimum frequency in MHz
          freq_max: 6000, # -f: Maximum frequency in MHz
          antenna_enable: bool = False, # -p: Antenna port power, True=Enable, False=Disable
          lna_gain: int = 0, # -l: RX LNA (IF) gain, 0-40dB, 8dB steps
          vga_gain: int = 0, # -g: RX VGA (baseband) gain, 0-62dB, 2dB steps
          num_samples: int = 8192, # -n: Number of samples per frequency, 8192-4294967296
          bin_width: int 1000000, # -w: FFT bin width (frequency resolution) in Hz
          one_shot: Optional[bool] = None, # -1: One shot mode
          num_sweeps: Optional[int] = None, # -N: Number of sweeps to perform. If not set it defaults to continous sweeps if not one_shot mode
          bin_out: Optional[bool] = None, # -B: binary output. Normalize only desirable if saving the result
          bin_invfft_out: Optional[bool] = None, # -I: binary inverse FFT output. Normalize only desirable if saving the result
          filename: Optional[str] = None # output file
):
    amp_enable = 1 if amp_enable else 0

    freq_min = fix_limits(freq_min, 0, 6000)
    freq_max = fix_limits(freq_max, 0, 6000)
    antenna_enable = 1 if antenna_enable else 0
    lna_gain = fix_limits(lna_gain, 0, 40)
    vga_gain = fix_limits(vga_gain, 0, 62)
    num_samples = fix_limits(num_samples,8192, 4294967296)
    

    parameters_dict = {'-d': serial_number,
                       '-a': 1 if amp_enable else 0,
                       '-f': f'{freq_min}:{freq_max}',
                       '-p': antenna_enable,
                       '-l': lna_gain,
                       '-g': vga_gain,
                       '-n': num_samples, 
                       '-w': bin_width,
                       '-1': one_shot,
                       '-N': num_sweeps,
                       '-B': bin_out,
                       '-I': bin_invfft_out,
                       '-r': filename,                       
}

    parameters_dict = {k:v for k,v in parameters_dict.items() if v is not None}


# send('-h')

send('-1')

send('-f=88:108 -w=10000 -N=10')

send(DISCONNECT_MSG)

# while True:
#     msg = client_socket.recv(4080)
#     print(msg)