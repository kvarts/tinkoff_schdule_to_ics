FROM python:3.7.3-alpine

RUN apk update && apk add libressl-dev gcc musl-dev libffi-dev

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3", "index.py"]