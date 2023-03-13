import os
import json
import requests
import uuid

from celery import Celery

from queue_system import QueueManager


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')


stable_diffusion_url = "http://host.docker.internal:7000"

queue_manager = QueueManager(host="redis", port=6379)

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
#celery_app = Celery("tasks", broker="redis://172.17.0.1:6379/0", backend="redis://172.17.0.1:6379/0")

@celery_app.task(name="send_to_txt2img", time_limit=120, soft_time_limit=118)
def send_to_txt2img(ticket, json_data):
    try:
        response = requests.post(f"{stable_diffusion_url}/sdapi/v1/txt2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.dumps(json.loads(response)))
    finally:
        queue_manager.queue_remove(ticket)

@celery_app.task(name="send_to_img2img", time_limit=120, soft_time_limit=118)
def send_to_img2img(ticket, json_data):
    try:
        response = requests.post(f"{stable_diffusion_url}/sdapi/v1/img2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.loads(response))
    finally:
        queue_manager.queue_remove(ticket)

@celery_app.task(name="send_to_ctrl_net_txt2img", time_limit=120, soft_time_limit=118)
def send_to_txt2img(ticket, json_data):
    try:
        response = requests.post(f"{stable_diffusion_url}/controlnet/txt2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.dumps(json.loads(response)))
    finally:
        queue_manager.queue_remove(ticket)

@celery_app.task(name="send_to_ctrl_net_img2img", time_limit=120, soft_time_limit=118)
def send_to_txt2img(ticket, json_data):
    try:
        response = requests.post(f"{stable_diffusion_url}/controlnet/txt2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.dumps(json.loads(response)))
    finally:
        queue_manager.queue_remove(ticket)

@celery_app.task(name="get_image_ticket", time_limit=120, soft_time_limit=118)
def get_image_ticket():
    ticket = uuid.uuid4().hex
    queue_manager.queue_append(ticket)
    return ticket

@celery_app.task(name="get_stored_result", time_limit=120, soft_time_limit=118)
def get_stored_result(ticket):
    result = queue_manager.results_pop(ticket)
    if result is None:
        return {"data": None}
    return {"data": json.loads(result)}

@celery_app.task(name="get_queue_position", time_limit=120, soft_time_limit=118)
def get_queue_position(ticket):
    queue_index = queue_manager.queue_index(ticket)
    if queue_index is None:
        if queue_manager.results_get(ticket) is None:
            return {"queue_position": 0, "status": "nothing"}
        else:
            return {"queue_position": 0, "status": "ready"}
    else:
        return {"queue_position": queue_index + 1, "status": "waiting"}