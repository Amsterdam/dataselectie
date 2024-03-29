FROM python:3.11-slim-bullseye as builder
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install --no-install-recommends -y \
    curl \
    gdal-bin \
    libgeos-c1v5 \
    libpq5 \
    netcat-openbsd \
    build-essential \
    libgeos-dev \
    libpq-dev \
    python3-dev \
    libffi-dev

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Start runtime image
FROM python:3.11-slim-bullseye
RUN apt update && apt install --no-install-recommends -y \
    gdal-bin \
    libgeos-c1v5 \
    libpq5 \
    netcat-openbsd 

# Copy python build artifacts from builder image
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

RUN adduser --system datapunt
WORKDIR /app

RUN chown datapunt -R /app

EXPOSE 8000

USER datapunt

COPY dataselectie /app/

COPY .jenkins-import /.jenkins-import/

CMD /app/docker-entrypoint.sh
