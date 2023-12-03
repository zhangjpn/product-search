FROM python:3.10.13-alpine3.18
COPY ./requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY ./app/ /src/app/
COPY ./manage.py /src
COPY ./gunicorn.py /src
COPY ./manage.py /src
WORKDIR /src
EXPOSE 80
CMD gunicorn -c gunicorn.py "app.entry:create_app()"
