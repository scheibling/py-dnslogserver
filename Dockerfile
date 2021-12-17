FROM python:3-alpine

ENV DNSLOG_DOMAIN="localhost"
ENV DNSLOG_IP="0.0.0.0"

WORKDIR /app

COPY requirements.txt requirements.txt
COPY py-dnslogserver.py py-dnslogserver.py

RUN pip3 install -r requirements.txt
RUN mkdir /logging

EXPOSE 53/tcp
EXPOSE 53/udp
EXPOSE 80/tcp

ENTRYPOINT ["/bin/sh", "-c", "python /app/py-dnslogserver.py --dnslog-domain ${DNSLOG_DOMAIN} --dnslog-ip ${DNSLOG_IP} --logging-folder /logging", "--"]