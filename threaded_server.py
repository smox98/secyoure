from threading import Thread
import time, datetime, cv2, imutils, pickle, struct, socket
from imutils.video import VideoStream
from twilio.rest import Client

### Server port setup
UDP_IP = socket.gethostname()
UDP_PORT = 6969
LISTENING = (UDP_IP, UDP_PORT)

### Twilio client setup
auth_token  = "YOUR AUTH TOKEN"
account_sid = "YOUR ACCOUNT SID"
user_phone_number = "RECIPIENT #"
client_phone_number = "TWILIO #"
client = Client(account_sid, auth_token)
last_message_time = None

class ServerMaster(object):
    def __init__(self, src=0):
        self.stream = VideoStream(src=0).start()
        self.display_frame = None
        # Start the thread to read frames from the video stream
        self.video_thread = Thread(target=self.update, args=())
        self.video_thread.daemon = True
        self.video_thread.start()
        # Start the thread to send frames to clients
        self.server_thread = Thread(target=self.broadcast, args=())
        self.server_thread.daemon = True
        self.server_thread.start()

    def server_setup(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(LISTENING)
        s.listen()
        return s

    def broadcast(self):
        s = self.server_setup()
        clientsocket, address = s.accept()
        data = clientsocket.recv(400)
        print(data.decode("utf-8"))
        print(address)
        try:
            while True:
                if self.display_frame.all() != None:
                    data = pickle.dumps(self.display_frame)
                    message_size = struct.pack("L", len(data))
                    clientsocket.sendall(message_size + data)
        except:
            print("Disconnected")
            self.broadcast()

    def update(self):
        # Read the next frame from the stream in a different thread
        first_frame = None
        last_message_time = None
        time.sleep(2)
        while True:
            # Read in the next frame from video feed
            frame = self.stream.read()

            # Apply some ill mods to current frame and show it
            display_frame = imutils.resize(frame, width=1000)
            frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame, (25, 25), 0)

            if first_frame is None: # Initialize first_frame in the first iteration of the loop
                first_frame = frame

            # Check for diff between current and first frame 
            frame_delta = cv2.absdiff(first_frame, frame)
            delta_threshold = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

            # Get contours from delta of the two frames (the "motion")
            delta_threshold = cv2.dilate(delta_threshold, None, iterations=2)
            contours = cv2.findContours(delta_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)

            text = "No Motion"
            max_area = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                max_area = area if area > max_area else max_area
                if area < 6000:
                    continue
                (a, b, c, d) = cv2.boundingRect(contour)
                cv2.rectangle(display_frame, (a,b), (a+c, b+d), (0,255,0), 2)
                text = "Motion"

            cv2.putText(display_frame, "Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # send text message
            if text == "Motion" and (last_message_time == None or 
            datetime.datetime.now() > last_message_time + datetime.timedelta(minutes = 1)):
                last_message_time = datetime.datetime.now()
                message = client.messages.create(
                            to=user_phone_number, 
                            from_=client_phone_number,
                            body="Motion detected!")

            self.display_frame = display_frame

    def show_frame(self):
        # Display frames in main program
        if self.display_frame.all() != None:
            cv2.imshow('frame', self.display_frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                self.stream.stop()
                cv2.destroyAllWindows()
                exit(1)

if __name__ == '__main__':
    threaded_server_instance = ServerMaster()
    while True:
        try:
            threaded_server_instance.show_frame()
        except AttributeError:
            pass