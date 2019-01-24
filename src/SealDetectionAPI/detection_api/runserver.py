# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from task_management.api_task import ApiTaskManager
from flask import Flask, request, send_file, abort
from flask_restful import Resource, Api
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EWrapper
from PIL import Image
import sys
sys.path.append('../SealDetectionRCNN')
import api as sealapi
from io import BytesIO
from os import getenv

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream', 'image/jpeg']

api_prefix = getenv('API_PREFIX')
app = Flask(__name__)
api = Api(app)

# Log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the internal-container AI for Earth Task Manager (not for production use!).
api_task_manager = ApiTaskManager(flask_api=api, resource_prefix=api_prefix)

ai4e_wrapper = AI4EWrapper(app)


# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
det = sealapi.SealDetector('/app/models/seals-detection-ir-n-large-86.0/fasterrcnn_07281142_0.8598245413189538', True)

# API Key, which is required to use the API
with open('seals_api_key.txt', 'rt') as fi:
    api_key = fi.read().strip()

# Healthcheck endpoint - this lets us quickly retrieve the status of your API.
@app.route('/', methods=['GET'])
def health_check():
    return "Health check OK"

# POST, sync API endpoint example
@app.route(api_prefix + '/detect', methods=['POST'])
def post():
    if not request.headers.get("Content-Type") in ACCEPTED_CONTENT_TYPES:
        print("Received file type " + request.headers.get("Content-Type"))
        return abort(415, "Unable to process request. Only png or jpeg files are accepted as input")
    elif not api_key == request.values.get('api_key', '').strip():
        return abort(403, 'Invalid API key')

    image = BytesIO(request.data)
    return ai4e_wrapper.wrap_sync_endpoint(detect, "post:detect", image_bytes=image)

def detect(**kwargs):
    print('runserver.py: detect() called...')
    image_bytes = kwargs.get('image_bytes', None)

    test_image = Image.open(image_bytes)
    pred_bboxes, pred_scores = det.predict_image(test_image, 1000)
    #pred_img = visdom_bbox(np.array(test_image.convert('RGB')).transpose((2, 0, 1)),
    #                at.tonumpy(pred_bboxes[:,[1,0,3,2]]),
    #                at.tonumpy([1 for _ in pred_bboxes]),
    #                at.tonumpy(pred_scores),
    #                label_names=['Animal', 'BG'])
    #PIL.Image.fromarray((255*pred_img).transpose((1,2,0)).astype(np.uint8)).save('output.jpg')

    return serve_pil_image(det.annotate_image(test_image, 5))


# GET, sync API endpoint example
@app.route(api_prefix + '/echo/<string:text>', methods=['GET'])
def echo(text):
    # wrap_sync_endpoint wraps your function within a logging trace.
    return ai4e_wrapper.wrap_sync_endpoint(my_sync_function, "GET:echo", echo_text=text)

def my_sync_function(**kwargs):
    echo_text = kwargs.get('echo_text', '')
    return 'Echo: ' + echo_text

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=90)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run()
