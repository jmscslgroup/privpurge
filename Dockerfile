FROM python:3.8.0-slim

RUN apt-get update

WORKDIR /install

COPY requirements.txt .
COPY setup.py .
COPY privpurge/ privpurge

RUN python -m pip install .

RUN adduser --system --group --shell /bin/sh auser
USER auser

WORKDIR /data

ENTRYPOINT ["privpurge"]