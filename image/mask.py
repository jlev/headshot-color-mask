import numpy as np
import cv2
import os


DEBUG = True

MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10

def rect(image, rect):
    if DEBUG:
        print(rect)
        cv2.imwrite('output/mask_in.png', image)
   
    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, rect, background, foreground, 1, cv2.GC_INIT_WITH_RECT)

    black_mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    masked_image = image*black_mask[:,:,np.newaxis]

    if DEBUG:
        cv2.imwrite('output/mask_black.png', masked_image)

    #to save the image without black background
    tmp = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(masked_image)
    rgba = [b,g,r, alpha]
    image_threshold = cv2.merge(rgba,4)

    if DEBUG:
        cv2.imwrite('output/mask_alpha.png', image_threshold)

    return image_threshold 
