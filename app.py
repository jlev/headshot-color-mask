import os
from flask import Flask, request, render_template, make_response, send_from_directory
from flask.json import JSONEncoder
from flask import jsonify

import image
from image import convert, detect, mask

templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=templates)

# weird trick to get flask to handle numpy int types
class NumpyJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return convert.cv_to_json(obj)
        except TypeError:
            return JSONEncoder.default(self, obj)
app.json_encoder = NumpyJSONEncoder

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/image/mask', methods=['POST'])
def image_mask():
    data = request.form.to_dict()
    image = convert.data_uri_to_cv(data.get('image'))

    face = detect.face(image)
    if not face:
        return make_response(jsonify({'error': 'no faces found'}), 400)
    masked = mask.grab(image, face)
    
    eyes = detect.eyes(image)
    if not eyes:
        eyes = []
       # return make_response(jsonify({'error': 'no eyes found'}), 400)
    corners = detect.face_rect_corners(face, radius=20, padding=40)
    probable_points = eyes + corners

    refined = mask.refine(masked, probable_points)
    refined_alpha = mask.blackToAlpha(refined)
    return jsonify({'image': convert.cv_to_data_uri(refined_alpha)})

@app.route('/image/refine', methods=['POST'])
def image_refine():
    data = request.form.to_dict()
    image = convert.data_uri_to_cv(data.get('image'))
    rect = data.get('rect')
    points = data.get('points')

    refined = mask.refine(masked, rect, points)
    refined_alpha = mask.blackToAlpha(refined)
    return jsonify({'image': convert.cv_to_data_uri(refined_alpha)})

if __name__ == "__main__":
    app.run(debug=True)