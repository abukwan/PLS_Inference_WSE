# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
RUN python3 -m pip install --upgrade pip
RUN apt-get update
RUN apt-get install -y vim
WORKDIR /PLSComment
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "PLS_keywords.py"]
