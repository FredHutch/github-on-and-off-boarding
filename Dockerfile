FROM ubuntu:16.04

RUN apt-get update -y && apt-get install -y python3 python3-pip

RUN pip3 install pipenv

COPY app.py /app/

COPY wsgi.py /app/

WORKDIR /app

COPY Pipfile* /app/

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pipenv install --system

EXPOSE 8000

COPY run.sh /app/

# FIXME : CMD should source GITHUB_ORG and GITHUB_TOKEN from secrets files

CMD ./run.sh
