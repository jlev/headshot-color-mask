import cv2
import numpy as np
import math

DEBUG = True

faceCascade = cv2.CascadeClassifier("image/haarcascade_frontalface_default.xml")
eyesCascade = cv2.CascadeClassifier("image/haarcascade_eye_tree_eyeglasses.xml")

def face(orig_image):
    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
    if DEBUG:
        cv2.imwrite('output/face_in.png', image)

    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    if DEBUG:
        print(f'found {len(faces)} faces')

    if len(faces) == 0:
        return None

    # determine face matched rectangles
    rect = ()
    for (x, y, w, h) in faces:
        pad_x = math.floor(w*0.5) # expand width by 50%
        pad_y = math.floor(h*0.4) # expand height by 40%
        rect = (x-pad_x, y-pad_y, x+w+pad_x, y+h+pad_y)

    if DEBUG:
        cv2.rectangle(image, (rect[0], rect[1]), (rect[2], rect[3]) , (255, 255, 255), 2)
        cv2.imwrite('output/face_detect.png', image)
        
    return rect

def eyes(orig_image):
    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
    if DEBUG:
        cv2.imwrite('output/eyes_in.png', image)

    eyes = eyesCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if DEBUG:
        print(f'found {len(eyes)} eyes')

    # determine face matched rectangles
    circles = []
    for (x, y, w, h) in eyes:
        r = math.ceil((w+h)*0.25)
        # we are pretty darn sure the eyes are foreground
        circles.append((x+r, y+r, r, cv2.GC_FGD))

        if DEBUG:
            cv2.circle(image, (x+r,y+r), r, (255, 255, 255), 2)

    if DEBUG:
        cv2.imwrite('output/eyes_detect.png', image)
        
    return circles

def face_rect_corners(rect, radius=20, padding=0):
    # take a CV rectangle, return a list of small circles at the corners (optionally padded in)
    # as x,y,r,c
    circles = []

    # rect is x_left, y_top, x_right, y_bottom
    # line down from top left, probable background
    circles.append((rect[0]+padding, rect[1]+padding, radius, cv2.GC_PR_BGD))
    # line down from top right, probable background
    circles.append((rect[2]-padding, rect[1]+padding, radius, cv2.GC_PR_BGD))
    # bottom left, probable foreground
    circles.append((rect[0]+padding, rect[3]-padding, radius, cv2.GC_FGD))
    # bottom right, probable foreground
    circles.append((rect[2]-padding, rect[3]-padding, radius, cv2.GC_FGD))

    return circles