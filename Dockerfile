FROM python:alpine

RUN apk add --no-cache \
  nano \
  ffmpeg \
  tzdata

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/
RUN apk --update-cache add --virtual build-dependencies gcc libc-dev make \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del build-dependencies

COPY . /app

EXPOSE 8080

VOLUME ["/youtube-dl"]

CMD [ "python", "-u", "./youtube-dl-server.py" ]
