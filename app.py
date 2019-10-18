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
  eyes = detect.eyes(image)

  if not face:
    return make_response(jsonify({'error': 'no faces found'}), 400)

  masked = mask.grab(image, face, eyes)
  return jsonify({'image': convert.cv_to_data_uri(masked)})

# @app.route('/image/refine', methods=['POST'])
# def image_refine():
#   data = request.get_json()
#   new_file = mask.refine(data['image'], data['rect_coords'], data['drawing'])
#   return jsonify()

if __name__ == "__main__":
    app.run(debug=True)