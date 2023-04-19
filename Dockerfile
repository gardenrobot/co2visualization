FROM alpine:3.17

RUN mkdir /app
WORKDIR /app

RUN apk update --no-cache && apk add tzdata libusb py3-hidapi python3 py3-pip

# TODO move to config, and it read it in through docker-compose, not the dockerfile
ENV TZ="America/New_York"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
