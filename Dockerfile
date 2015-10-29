FROM library/python:3.4

ENV PYTHONUNBUFFERED 1

RUN mkdir /web
WORKDIR /web

ADD requirements.txt /web/
RUN pip install -r requirements.txt

EXPOSE 8000

CMD uwsgi --ini uwsgi.conf

