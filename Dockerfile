FROM ubuntu:latest
LABEL authors="imFle"

ENTRYPOINT ["top", "-b"]
FROM python:3.11
WORKDIR /ACC
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "multiprocess.py"]