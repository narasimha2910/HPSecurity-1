FROM python:3.8.2-buster

WORKDIR /usr/workspace

COPY requirements.txt ./

RUN cat requirements.txt | xargs -n 1 -L 1 pip install

COPY . ./

CMD ["python", "run.py"]

EXPOSE 5000

LABEL Name="DCS Appserver" \
    VERSION="1.0.0"