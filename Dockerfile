FROM library/python:2.7.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /web
WORKDIR /web

ADD requirements.txt /web/
RUN pip install -r requirements.txt

EXPOSE 80

CMD gunicorn --config gunicorn.py wsgi:application

