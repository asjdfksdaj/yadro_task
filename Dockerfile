FROM python:3.11-slim

WORKDIR /fastapi-dag-service

COPY requirements.txt /fastapi-dag-service/
RUN pip install -r requirements.txt

COPY app/ /fastapi-dag-service/app/
COPY tests/ /fastapi-dag-service/tests/


CMD uvicorn app.main:app --host 0.0.0.0 --port 8080