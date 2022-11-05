FROM python:3.8-slim

RUN useradd -m ctf

WORKDIR /app

COPY src/ .

ENV PORT 1337
RUN apt update -y
RUN apt install curl -y
RUN apt install netcat -y
RUN apt install ncat -y
RUN pip3 install --upgrade --no-cache-dir -r requirements.txt
RUN apt install unzip -y


RUN chown -R root:ctf /app && \
    chmod 750 /app /app/main.py

USER ctf

CMD ["/usr/local/bin/python", "/app/main.py"]

EXPOSE 1337