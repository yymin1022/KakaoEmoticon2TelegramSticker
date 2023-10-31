FROM python:3.12.0

WORKDIR /app
ADD ./ /app

ENV DEBIAN_FRONTEND=noninteractive

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]