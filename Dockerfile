FROM ubuntu:16.04

RUN apt-get update -y && apt-get install -y python3 python3-pip

COPY app.py /app/

COPY wsgi.py /app/

WORKDIR /app

COPY requirements.txt /app/

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip3 install -r requirements.txt

EXPOSE 8000

COPY run.sh /app/

CMD ["/bin/sh", "-c", "GITHUB_ORG=`cat /run/secrets/GITHUB_ORG` GITHUB_TOKEN=`cat /run/secrets/GITHUB_TOKEN` ./run.sh"]
