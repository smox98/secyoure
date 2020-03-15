import socket
import cv2
import struct
import pickle

UDP_IP = socket.gethostname()
UDP_PORT = 8080
LISTENING = (UDP_IP, UDP_PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(LISTENING)
s.listen()

clientsocket, address = s.accept()

data = clientsocket.recv(400)
print(data.decode("utf-8"))
print(address)

cap = cv2.VideoCapture(0)
cap.set(3, 500)
cap.set(4, 600)

while True:
    ret, frame = cap.read()
    data = pickle.dumps(frame)
    message_size = struct.pack("L", len(data))
    clientsocket.sendall(message_size + data)

cap.release()

