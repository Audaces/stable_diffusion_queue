# syntax=docker/dockerfile:1

FROM python:3

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /python-docker/flask_app

RUN python3 -m celery -A tasks worker -l INFO --concurrency=1 --detach
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "wsgi:app", "--capture-output", "--log-level", "debug"]

EXPOSE 7000