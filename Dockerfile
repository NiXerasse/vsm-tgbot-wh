FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc libxml2-dev libxslt-dev \
    libcairo2 libpango1.0-0 libjpeg62-turbo-dev libpng-dev \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
