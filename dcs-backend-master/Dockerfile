FROM python:3.8.2-buster

WORKDIR /usr/workspace

COPY requirements.txt ./

RUN cat requirements.txt | xargs -n 1 -L 1 pip install

COPY . ./

RUN mkdir -p /usr/workspace/toProcess

RUN mkdir -p /usr/workspace/processed

RUN apt-get update && apt-get install -y ffmpeg

CMD ["tail", "-f", "/dev/null"]