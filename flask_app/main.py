import json

from flask import Flask, request, Response, make_response
from flask_cors import CORS

from tasks import send_to_txt2img, send_to_img2img, get_queue_position, get_stored_result, get_image_ticket

app = Flask(__name__)
CORS(app)

@app.route("/queue/v1/txt2img", methods=["POST"])
def enqueue_txt2img():
    ticket = get_image_ticket()
    send_to_txt2img.delay(ticket, json.dumps(request.json))

    response = make_response({"task_id": ticket}, 202)
    response.headers["Location"] = "/queue/status"
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/queue/v1/img2img", methods=["POST"])
def enqueue_img2img():
    ticket = get_image_ticket()
    send_to_img2img.delay(ticket, json.dumps(request.json))

    response = make_response({"task_id": ticket}, 202)
    response.headers["Location"] = "/queue/status"
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/queue/status", methods=["GET"])
def queue_size():
    ticket = request.args.get("task_id")
    return get_queue_position(ticket)

@app.route("/generated_image", methods=["GET"])
def get_generated_image():
    ticket = request.args.get("task_id")
    result = get_stored_result(ticket)
    if result is None:
        return Response({"Error": "Error: Could not get stored result"}, status=404, headers={"Content-Type": "application/json"})
    return Response(result, headers={"Content-Type": "application/json"})