FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install build-essential for small C extensions (webrtcvad) + multimedia libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install dlib prebuilt binary wheel (no dlib compilation!)
RUN pip install --no-cache-dir dlib-bin

# Install face-recognition without pulling raw dlib source
RUN pip install --no-cache-dir --no-deps face-recognition

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 0 myproject.wsgi:application
