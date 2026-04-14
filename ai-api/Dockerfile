FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir ".[test]"

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8001
