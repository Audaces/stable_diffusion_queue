# syntax=docker/dockerfile:1

FROM python:3

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 7860
ENV DEBUG true

COPY . /flask_app
WORKDIR /flask_app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "wsgi:app", "--capture-output", "--log-level", "debug"]