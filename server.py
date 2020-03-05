import cv2
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read() # read in the next frame from video feed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # apply gray filter to the frame
    cv2.imshow('frame',gray)    # show the modified frame

    # Listen for 'q' keypress to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()