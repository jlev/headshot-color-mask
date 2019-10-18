import cv2
import numpy as np
import math

DEBUG = True

cascadePath = "image/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)


def face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if DEBUG:
        cv2.imwrite('output/face_in.png', image)
        cv2.imwrite('output/face_gray.png', gray)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # determine face matched rectangles
    rect = ()
    for (x, y, w, h) in faces:
        pad_x = math.floor(w*0.5) # expand width by 50%
        pad_y = math.floor(h*0.4) # expand height by 40%
        rect = (x-pad_x, y-pad_y, x+w+pad_x, y+h+pad_y)

    if DEBUG:
        print(rect)
        cv2.rectangle(image, (rect[0], rect[1]), (rect[2], rect[3]) , (255, 255, 255), 2)
        cv2.imwrite('output/face_detect.png', image)
        
    return rect