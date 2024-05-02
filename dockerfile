FROM python:3.12-slim
LABEL maintainer="Jacob Danell <jacob@emberlight.se>"

RUN apt update \
    && apt install -y --no-install-recommends iputils-ping \
    && apt autoclean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/bin

VOLUME /usr/local/bin/wol

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /usr/local/bin/wol/

EXPOSE 8080

CMD ["python", "/usr/local/bin/wol/main.py"]