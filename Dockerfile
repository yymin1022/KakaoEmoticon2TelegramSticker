FROM python:3.10.6

WORKDIR /app
ADD ./ /app

ENV DEBIAN_FRONTEND=noninteractive

RUN wget -O /tmp/chrome.deb https://www.slimjet.com/chrome/download-chrome.php?file=files%2F90.0.4430.72%2Fgoogle-chrome-stable_current_amd64.deb
RUN dpkg -i /tmp/chrome.deb
RUN apt update
RUN apt install --fix-broken -y

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]