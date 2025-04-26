FROM python:3.13.2-slim

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
