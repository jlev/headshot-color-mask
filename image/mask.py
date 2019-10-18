import numpy as np
import cv2
import os


DEBUG = True

def grab(image, rect, points):
    if DEBUG:
        cv2.imwrite('output/mask_in.png', image)

    width = image.shape[0]
    height = image.shape[1]

    # first pass just with face rect + padding
    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    mask, background, foreground = cv2.grabCut(image, mask, rect, background, foreground, 1, cv2.GC_INIT_WITH_RECT)

    # seed the mask with a list of points (x,y,radius,color)
    # color needs to be matched to GC_BGD (background), GC_FGD (foreground)
    for pt in points:
        x = int(pt[0])
        y = int(pt[1])
        r = pt[2]
        c = pt[3]
        if (x > width or x < 0) or (y > height or y < 0):
            continue
        if c not in [cv2.GC_BGD, cv2.GC_PR_BGD, cv2.GC_PR_FGD, cv2.GC_FGD]:
            # convert? nah
            print("incorrect color for point", pt)
            continue
        cv2.circle(mask, (x,y), r, c)

    # add probable background points on the corners?

    mask, background, foreground = cv2.grabCut(image, mask, rect, background, foreground, 1, cv2.GC_INIT_WITH_MASK)

    background_mask = np.where((mask==cv2.GC_PR_BGD)|(mask==cv2.GC_BGD),0,1).astype('uint8')
    masked_image = image*background_mask[:,:,np.newaxis]

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
