FROM python:3.13-slim

WORKDIR /app

COPY src/ ./src/
COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    apt-get install -y --no-install-recommends \
    vim \
    btop

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "src/Puente.py" ]
