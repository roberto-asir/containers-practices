# Base build
FROM python:3.10-alpine as base
RUN apk add --update --virtual .build-deps \
    build-base \
    postgresql-dev \
    python3-dev \
    libpq

COPY ./code/requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

# Now multistage build
FROM python:3.10-alpine
RUN apk add libpq

WORKDIR /code

COPY --from=base /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
COPY ./code /code/
COPY ./log.py /usr/local/lib/python3.10/site-packages/django/utils/log.py

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1

# ENV APP_PORT=9000
# ENV POSTGRES_DB=postgres
# ENV POSTGRES_USER=postgres
# ENV POSTGRES_PASSWORD=postgres


CMD python manage.py runserver 0.0.0.0:${APP_PORT}
