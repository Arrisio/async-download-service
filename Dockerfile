FROM python:3.8-slim-buster

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get update
RUN apt-get install -y zip

ADD requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --upgrade pip; \
    pip install -r requirements.txt;



