FROM python:3.7-slim-bullseye AS builder
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    libgeos-dev \
    libpq-dev \
    python3-dev \
    libffi-dev

COPY requirements* ./
ARG PIP_REQUIREMENTS=requirements.txt

RUN python -m pip install --upgrade pip setuptools
RUN python -m pip install --no-cache-dir -r $PIP_REQUIREMENTS

# Start runtime image,
FROM python:3.7-slim-bullseye
RUN python -m pip install --upgrade pip setuptools 
RUN apt update && apt install --no-install-recommends -y \
    curl \
    libgdal28 \
    libgeos-c1v5 \
    libpq5 \
    media-types \
    netcat-openbsd 

# Copy python build artifacts from builder image
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/

WORKDIR /app/

EXPOSE 8000
USER datapunt

COPY dataselectie /app/

COPY .jenkins-import /.jenkins-import/

CMD /app/docker-entrypoint.sh
