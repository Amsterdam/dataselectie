FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt

COPY dataselectie /app/
COPY get_imds_db_token.sh .

COPY .jenkins-import /.jenkins-import/

CMD /app/docker-entrypoint.sh
