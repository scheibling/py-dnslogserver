<h1 align="center">PY-DNSLogServer</h1>
<h4 align="center">A simple, one-file DNSLog server with HTTP endpoint for log retrieval</h4>

# Features
- Logs all DNS queries to a given IP
- Only requires two DNS records (A and NS)
- Can be used on a subdomain
- Supports TCP and UDP DNS requests
- Supports log retrieval via HTTP endpoint
- Docker image available
- Can be used with scheibling/py-log4j-vul-scanner for automatic testing

# Description
Our company had a need to assess the security of some internal systems, not wanting to use an external DNSLog-server for security and firewall reasons we created our own.

# Usage

## Preparations
For using the DNSLog-server, you will need to set up the following DNS records:

| Record name | Record type | Record value | Description |
|---|---|---|---|
| dnslog-ns.example.com | A | 1.2.3.4 | IP of the DNSLog-server, since most DNS won't let you set an IP address as a name server |
| dnslog.example.com | NS | dnslog-ns.example.com | Define the DNSLog-server as a name server for *.dnslog.example.com | 

## CLI
```python
$ python3 py-dnslogserver.py
[•] Python3 DNSLog Server
[•] Provided by https://github.com/scheibling
[•] Version 1.0
usage: py-dnslogserver.py [-h] -d DNSLOG_DOMAIN -i DNSLOG_IP [-f LOGGING_FOLDER]

options:
  -h, --help            show this help message and exit
  -d DNSLOG_DOMAIN, --dnslog-domain DNSLOG_DOMAIN (Required)
                        DNSLog domain to resolve
  -i DNSLOG_IP, --dnslog-ip DNSLOG_IP
                        The IP of this server for listeners (Required)
  -f LOGGING_FOLDER, --logging-folder LOGGING_FOLDER
                        Folder to store logs (Default: 'logging'-subdirectory)
```

## Docker

### Get the prebuilt image
```shell
# Run the image with logs to cli
docker run -it --rm --name py-dnslogserver -v ./logging:/logging --network host -e DNSLOG_DOMAIN=dnslog.domain.com -e DNSLOG_IP="1.2.3.4" -e PYTHONUNBUFFERED=1 scheibling/py-dnslogserver:latest

# Run the image as a daemon
docker run -it --rm --name py-dnslogserver -v ./logging:/logging --network host -e DNSLOG_DOMAIN=dnslog.domain.com -e DNSLOG_IP="1.2.3.4" -e PYTHONUNBUFFERED=1 scheibling/py-dnslogserver:latest
```
# Run the image with docker-compose
```yaml
version: "2.2"
services:
  dnslogserver:
    container_name: dnslogserver
    image: scheibling/py-dnslogserver:latest
    network_mode: host
    volumes:
        - ./logging:/logging:rw
    environment:
      - DNSLOG_DOMAIN=dnslog.domain.com
      - DNSLOG_IP=1.2.3.4
      - PYTHONUNBUFFERED=1
```
```shell
# Logging to stdout
sudo docker-compose up

# Logging to docker logs
sudo docker-compose up -d
```

```shell
### Compile your own image and run
git clone https://github.com/scheibling/py-dnslogserver.git
cd py-dnslogserver
sudo docker build -t py-dnslogserver .

# Run the image with logs to cli
docker run -it --rm --name py-dnslogserver -v ./logging:/logging --network host -e DNSLOG_DOMAIN=dnslog.domain.com -e DNSLOG_IP="1.2.3.4" -e PYTHONUNBUFFERED=1 py-dnslogserver

# Run the image as a daemon
docker run -it --rm --name py-dnslogserver -v ./logging:/logging --network host-e DNSLOG_DOMAIN=dnslog.domain.com -e DNSLOG_IP="1.2.3.4" -e PYTHONUNBUFFERED=1 py-dnslogserver

# Run the image with docker-compose
```yaml
version: "2.2"
services:
  dnslogserver:
    container_name: dnslogserver
    image: py-dnslogserver
    network_mode: host
    volumes:
        - ./logging:/logging:rw
    environment:
      - DNSLOG_DOMAIN=dnslog.domain.com
      - DNSLOG_IP=1.2.3.4
      - PYTHONUNBUFFERED=1
```


# Legal Disclaimer
This project is made for testing purposes only. Usage of py-dnslogserver for attacking targets without prior mutual consent could be illegal.


# License
The project is licensed under MIT License.