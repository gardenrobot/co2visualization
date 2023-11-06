FROM alpine:3.17

RUN mkdir /app
WORKDIR /app

RUN apk update --no-cache && apk add tzdata libusb py3-hidapi python3 py3-pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
