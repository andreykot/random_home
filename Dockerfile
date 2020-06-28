FROM python:3.8-slim-buster

MAINTAINER Andrey Kot "a.n.kot@yandex.ru"

RUN mkdir -p /usr/src/random_home
WORKDIR /usr/src/random_home

COPY . /usr/src/random_home

RUN pip install --no-cache-dir -r requirements.txt

CMD python3 run_bot.py