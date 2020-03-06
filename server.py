import time
import cv2
import imutils
from imutils.video import VideoStream

stream = VideoStream(src=0).start()
time.sleep(2.0)

first_frame = None
while True:
    # Read in the next frame from video feed
    frame = stream.read()

    # Apply some ill mods to current frame and show it
    frame = imutils.resize(frame, width=500)
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

    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        max_area = area if area > max_area else max_area
        if area < 1000:
            continue
        (a, b, c, d) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (a,b), (a+c, b+d), (0,255,0), 2)
    
    # Show the current frame
    cv2.imshow('frame', frame)
    print(max_area)

    # Listen for 'q' keypress to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
stream.release()
cv2.destroyAllWindows()