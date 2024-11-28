FROM python:3.9-slim

ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
COPY ../src/ ./src/

RUN pip install -r requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/tmp /app/logs /app/output /app/output/videos /app/output/previews

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 17778

CMD ["python", "/app/src/main.py"] 