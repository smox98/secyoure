import sys
import socket
import cv2 
import pickle
import struct
import numpy as np

PORT = int(sys.argv[1])
HOST = "localhost"
LISTENING_ADDRESS = (HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(LISTENING_ADDRESS)
print('Just created a socket')

#MESSAGE AS AN EXAMPLE
MESSAGE = "hello! from %s, port %s" % (HOST, s.getsockname()[1])
print("Message:", MESSAGE)

s.send(MESSAGE.encode("utf-8"))

packet_size = struct.calcsize("L")
data = b''

while True:
    while len(data) < packet_size:
        data += s.recv(4096)
    
    msg_size = data[:packet_size]
    data = data[packet_size:]
    msg_size_unpacked = struct.unpack("L", msg_size)[0]

    while len(data) < msg_size_unpacked:
        data += s.recv(4096)
    
    frame_data = data[:msg_size_unpacked]
    data = data[msg_size_unpacked:]

    frame = pickle.loads(frame_data)

    cv2.imshow('secyoure', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
    