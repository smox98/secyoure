import time
import datetime
import cv2
import imutils
from imutils.video import VideoStream
from twilio.rest import Client

stream = VideoStream(src=0).start()
time.sleep(2.0)

# Twilio client info
auth_token  = "f4c11db697cf94c3cb5b83d97be137ba"
account_sid = "ACb2e17172de740a87a9746fe80ec9cdc4"
user_phone_number = "4253208699"
client_phone_number = "+12522070623"
client = Client(account_sid, auth_token)
last_message_time = None

first_frame = None
while True:
    # Read in the next frame from video feed
    frame = stream.read()

    # Apply some ill mods to current frame and show it
    frame = imutils.resize(frame, width=1000)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
        if area < 5000:
            continue
        (a, b, c, d) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (a,b), (a+c, b+d), (0,255,0), 2)
        text = "Motion"
    

    cv2.putText(frame, "Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # send text message
    if text == "Motion" and (last_message_time == None or 
      datetime.datetime.now() > last_message_time + datetime.timedelta(minutes = 1)):
      last_message_time = datetime.datetime.now()
      message = client.messages.create(
        to=user_phone_number, 
        from_=client_phone_number,
        body="Motion detected!")

    # Show the current frame
    cv2.imshow('frame', frame)
    # print(max_area)

    # Listen for 'q' keypress to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
stream.release()
cv2.destroyAllWindows()
