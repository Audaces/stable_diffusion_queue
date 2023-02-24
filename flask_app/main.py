import json

from flask import Flask, request, Response, make_response, json
from flask_cors import CORS

from worker import celery

app = Flask(__name__)
# CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route("/queue/v1/txt2img", methods=["POST"])
def enqueue_txt2img():
    # if request.method == "OPTIONS":
    #     response = make_response("", 200)
    #     response.headers["Content-Type"] = "application/json"
    #     # response.headers["Access-Control-Allow-Origin"] = "*"
    #     # response.headers['Access-Control-Allow-Methods'] = 'POST'
    #     # response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    #     app.logger.debug(response)
    #     return response
    if request.method == "POST":
        app.logger.debug("CHEGOU")
        ticket = celery.send_task("get_image_ticket").get()
        app.logger.debug(ticket)
        app.logger.debug(request.json)
        celery.send_task("send_to_txt2img", args=[ticket, json.dumps(request.json)])

        response = make_response({"task_id": ticket}, 202)
        response.headers["Location"] = "/queue/status"
        response.headers["Content-Type"] = "application/json"
        # response.headers["Access-Control-Allow-Origin"] = "*"
        app.logger.debug(response)
        return response

@app.route("/queue/v1/img2img", methods=["POST"])
def enqueue_img2img():
    ticket = celery.send_task("get_image_ticket").get()
    celery.send_task("send_to_img2img", args=[ticket, json.dumps(request.json)])

    response = make_response({"task_id": ticket}, 202)
    # response.headers["Location"] = "/queue/status"
    # response.headers["Content-Type"] = "application/json"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    app.logger.debug(response)
    return response

@app.route("/queue/status", methods=["GET", "POST"])
def queue_size():
    # if request.method == "OPTIONS":
    #     response = make_response("", 200)
    #     response.headers["Content-Type"] = "application/json"
    #     # response.headers["Access-Control-Allow-Origin"] = "*"
    #     # response.headers['Access-Control-Allow-Methods'] = 'GET'
    #     # response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    #     app.logger.debug(response)
    #     return response
    if request.method == "GET":
        ticket = request.args.get("task_id")
        response = make_response(celery.send_task("get_queue_position", args=[ticket]).get(), 200)
        response.headers["Content-Type"] = "application/json"
        # response.headers["Access-Control-Allow-Origin"] = "*"
        app.logger.debug(response)
        return response
    if request.method == "POST":
        ticket = request.args.get("task_id")
        response = make_response(celery.send_task("get_queue_position", args=[ticket]).get(), 200)
        response.headers["Content-Type"] = "application/json"
        # response.headers["Access-Control-Allow-Origin"] = "*"
        app.logger.debug(response)
        return response

@app.route("/generated_image", methods=["GET", "POST"])
def get_generated_image():
    ticket = request.args.get("task_id")
    result = celery.send_task("get_stored_result", args=(ticket,)).get()
    if result["data"] is None:
        return Response(json.dumps({"Error": "Error: Could not get stored result"}), status=404, headers={"Content-Type": "application/json"})
    return Response(json.dumps(result["data"]), headers={"Content-Type": "application/json"})