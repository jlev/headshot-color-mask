import numpy as np
import cv2
import os


DEBUG = True

def grab(image, rect):
    if DEBUG:
        cv2.imwrite('output/mask_in.png', image)

    # first pass just with face rect + padding
    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    mask, background, foreground = cv2.grabCut(image, mask, rect, background, foreground, 1, cv2.GC_INIT_WITH_RECT)

    # temp export
    background_mask = np.where((mask==cv2.GC_PR_BGD)|(mask==cv2.GC_BGD),0,1).astype('uint8')
    masked_image = image*background_mask[:,:,np.newaxis]
    if DEBUG:
        cv2.imwrite('output/mask_black.png', masked_image)

    return masked_image

def refine(image, rect, points):
    image_width = image.shape[0]
    image_height = image.shape[1]

    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)

    # seed the mask with a list of points (x,y,radius,color)
    # color needs to be matched to GC_BGD (background), GC_FGD (foreground)
    for pt in points:
        x = int(pt[0])
        y = int(pt[1])
        r = pt[2]
        c = pt[3]
        if (x > image_width or x < 0) or (y > image_height or y < 0):
            continue
        if c not in [cv2.GC_BGD, cv2.GC_PR_BGD, cv2.GC_PR_FGD, cv2.GC_FGD]:
            # convert? nah
            print("incorrect color for point", pt)
            continue
        cv2.circle(mask, (x,y), r, c)

    # add probable points on the corners
    pad_dist = 10 # px offset
    rect_width = rect[2] - rect[0]
    rect_height = rect[3] - rect[1]
    print('width', rect_width)
    print('height', rect_height)
    fill = -1 # flag 
    # top left, probable background
    cv2.circle(mask, (rect[0]+pad_dist, rect[1]+pad_dist), pad_dist, cv2.GC_PR_BGD, fill)
    # top right, probable background
    cv2.circle(mask, (rect[2]-pad_dist, rect[3]-rect_height+pad_dist), pad_dist, cv2.GC_PR_BGD, fill)
    # bottom left, probable foreground
    cv2.circle(mask, (rect[2]-rect_width+pad_dist, rect[3]-pad_dist), pad_dist, cv2.GC_PR_FGD, fill)
    # bottom right, probable foreground
    cv2.circle(mask, (rect[2]-pad_dist, rect[3]-pad_dist), pad_dist, cv2.GC_PR_FGD, fill)

    mask, background, foreground = cv2.grabCut(image, mask, rect, background, foreground, 1, cv2.GC_INIT_WITH_MASK)
    background_mask = np.where((mask==cv2.GC_PR_BGD)|(mask==cv2.GC_BGD),0,1).astype('uint8')
    masked_image = image*background_mask[:,:,np.newaxis]
    if DEBUG:
        cv2.imwrite('output/mask_refine_black.png', masked_image)

    # threshold remove the black background
    tmp = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(masked_image)
    rgba = [b,g,r, alpha]
    image_threshold = cv2.merge(rgba,4)

    if DEBUG:
        cv2.imwrite('output/mask_refine_alpha.png', image_threshold)

    return image_threshold 
