FROM python:3.8.0-slim as builder

RUN apt-get update

WORKDIR /install

COPY requirements.txt .
COPY setup.py .
COPY privpurge/ privpurge

RUN python -m pip install --user -v .


# Production

FROM python:3.8.0-slim as app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /data

ENTRYPOINT ["privpurge"]