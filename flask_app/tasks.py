import json
import requests
import uuid

from celery import Celery

stable_diffusion_url = "177.36.181.226:7860"

from queue_system import QueueManager

queue_manager = QueueManager(host="172.17.0.1", port=6379)

celery_app = Celery("tasks", broker="redis://172.17.0.1:6379/0", backend="redis://172.17.0.1:6379/0")

def get_image_ticket():
    ticket = uuid.uuid4().hex
    queue_manager.queue_append(ticket)
    return ticket

@celery_app.task(time_limit=120, soft_time_limit=118)
def send_to_txt2img(ticket, json_data):
    links = json.loads(requests.get("http://henriquec.pythonanywhere.com/links").text)

    try:
        response = requests.post(f"{stable_diffusion_url}/sdapi/v1/txt2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.dumps(json.loads(response)))
    finally:
        queue_manager.queue_remove(ticket)

@celery_app.task(time_limit=120, soft_time_limit=118)
def send_to_img2img(ticket, json_data):
    links = json.loads(requests.get("http://henriquec.pythonanywhere.com/links").text)

    try:
        response = requests.post(f"{stable_diffusion_url}/sdapi/v1/img2img", data=json_data, headers={"Content-Type": "application/json"}, timeout=120).content
    except requests.exceptions.RequestException as exception:
        print("Error on POST request to stable diffusion")
        print(exception)
    else:
        queue_manager.results_set(ticket, json.loads(response))
    finally:
        queue_manager.queue_remove(ticket)

def get_stored_result(ticket):
    result = queue_manager.results_pop(ticket)
    if result is None:
        return
    return result

def get_queue_position(ticket):
    queue_index = queue_manager.queue_index(ticket)
    if queue_index is None:
        if queue_manager.results_get(ticket) is None:
            return {"queue_position": 0, "status": "nothing"}
        else:
            return {"queue_position": 0, "status": "ready"}
    else:
        return {"queue_position": queue_index + 1, "status": "waiting"}
