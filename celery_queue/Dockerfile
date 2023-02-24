# syntax=docker/dockerfile:1

FROM python:3

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

COPY . /celery_queue
WORKDIR /celery_queue

RUN pip install -U setuptools pip
RUN pip install -r requirements.txt