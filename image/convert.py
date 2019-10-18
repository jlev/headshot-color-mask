import cv2
import numpy as np
import base64
import json

def data_uri_to_cv(uri):
    encoded_data = uri.split(',')[1]
    np_arr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def cv_to_data_uri(image):
    retval, buffer = cv2.imencode('.png', image)
    encoded = base64.b64encode(buffer)
    return encoded

def cv_to_json(obj):
    # converts numpy arrays to json serializable strings
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    if isinstance(obj, bytes):
        # TODO, there must be a better way to convert bytes back to a string...
        prefix = "data:image/png;base64,"
        base64_str = str(obj).replace("b'", "").replace("'","")
        return prefix+base64_str
    raise TypeError('Not a cv2 object:', type(obj))

def cv_rect_to_canvas(arr):
    # cv rect is x1,y1,x2,y2
    # canvas is x,y,width,height

    x = arr[0]
    y = arr[1]
    w = arr[2]-x
    h = arr[3]-y

    return (x,y,w,h)

def canvas_rect_to_cv(str):
    arr = []
    for val in str.split(','):
        arr.append(int(val))
    return tuple(arr)