import numpy as np
import cv2
import os

ITERATIONS = 5
DEBUG = True

def blackToAlpha(image):
    # threshold to remove a black background
    tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(image)
    rgba = [b,g,r, alpha]
    masked_image = cv2.merge(rgba,4)
    return masked_image

def grab(image, rect):
    if DEBUG:
        cv2.imwrite('output/mask_in.png', image)

    # first pass just with just rect guide
    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, rect, background, foreground, ITERATIONS, cv2.GC_INIT_WITH_RECT)

    # apply mask to image and export
    background_mask = np.where((mask==cv2.GC_PR_BGD),0,1).astype('uint8')
    masked_image = image*background_mask[:,:,np.newaxis]
    if DEBUG:
        cv2.imwrite('output/mask_black.png', masked_image)

    return masked_image

def refine(image, points):
    # second pass using points list flagged as foreground or background

    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)

    # draw list of points (x,y,radius,color) as circles
    fill = -1 # flag
    image_width = image.shape[1]
    image_height = image.shape[0]
    for pt in points:
        x = int(pt[0])
        y = int(pt[1])
        r = pt[2]
        c = pt[3]
        if (x > image_width or x < 0) or (y > image_height or y < 0):
            print("point outside image", pt)
            continue
        if c not in [cv2.GC_BGD, cv2.GC_PR_BGD, cv2.GC_PR_FGD, cv2.GC_FGD]:
            print("incorrect color for point", pt)
            continue
        cv2.circle(mask, (x,y), r, c, fill)

    # do grabcut with points, but no rectangle
    cv2.grabCut(image, mask, None, background, foreground, ITERATIONS, cv2.GC_INIT_WITH_MASK)
    background_mask = np.where((mask==cv2.GC_PR_BGD),0,1).astype('uint8')
    masked_image = image*background_mask[:,:,np.newaxis]

    if DEBUG:
        cv2.imwrite('output/refine_black.png', masked_image)
    
        # convert GC flags back to visible grays
        # tmp to visualize mask seed
        viz_mask = np.zeros(image.shape[:2], np.uint8)
        viz_mask[mask == cv2.GC_BGD] = 25
        viz_mask[mask == cv2.GC_PR_BGD] = 50
        viz_mask[mask == cv2.GC_PR_FGD] = 200
        viz_mask[mask == cv2.GC_FGD] = 255
        cv2.imwrite('output/refine_viz.png', viz_mask)

    return masked_image


