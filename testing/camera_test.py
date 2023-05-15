import sys, time, math, os
import cv2
from imutils.video import WebcamVideoStream

cap = None
fps_record = []

threaded = False

if __name__ == '__main__':
    if threaded:
        cap = WebcamVideoStream(src=0).start()
    else:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 60)

    start_time = time.time()
    frame_count = 0
    display_time = 2
    fps = 0

    while True:
        if threaded: frame = cap.read()
        else: frame = cap.read()[1]

        frame_count += 1
        currentTime = time.time() - start_time
        if (currentTime) >= display_time :
            fps = frame_count / (currentTime)
            frame_count = 0
            start_time = time.time()
            fps_record.append(fps)

        cv2.putText(frame, "FPS: " + str(round(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Camera Test", frame)

        if cv2.waitKey(1) == 27:
            break

    print("Average FPS: " + str(round(sum(fps_record) / len(fps_record))))

    cap.release() if not threaded else cap.stop()
    cv2.destroyAllWindows()