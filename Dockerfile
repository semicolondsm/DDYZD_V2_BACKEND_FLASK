FROM python:3.8.7-buster

EXPOSE 8888

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "manage:app", "--bind", "0.0.0.0:8888", "-k", "gevent", "--access-logfile", "./logs/access.log", "--error-logfile", "./logs/error.log", "-w", "1"]