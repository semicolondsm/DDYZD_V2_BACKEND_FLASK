FROM python:3.7.9-buster

EXPOSE 8888

COPY . /app

WORKDIR /app

ENTRYPOINT ["gunicorn", "manage:app", "--bind", "0.0.0.0:8888"] 
