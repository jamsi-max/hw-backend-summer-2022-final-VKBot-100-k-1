FROM python:3.9-alpine3.13
LABEL maintainer="VKBot-100-k-1"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY bot/requirements.txt /requirements.txt
COPY bot/app /app
COPY bot/scripts /scripts

WORKDIR /app
EXPOSE 8080

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --upgrade setuptools && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home kts && \
    chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER kts

CMD ["run.sh"]
