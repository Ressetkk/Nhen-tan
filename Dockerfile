FROM python:alpine
LABEL maintainer="Ressetkk"
ARG VERSION
ENV VERSION=$VERSION

WORKDIR /bot
ADD ./requirements.txt .
RUN apk add --no-cache --virtual .build-deps build-base && \
    pip install -r requirements.txt && \
    apk del --no-cache .build-deps

COPY . .

CMD ["/usr/local/bin/python", "bot.py"]