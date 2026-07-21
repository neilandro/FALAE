FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 MPLCONFIGDIR=/tmp/matplotlib
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN mkdir -p /app/uploads /app/logs && useradd --create-home --shell /usr/sbin/nologin falae && chown -R falae:falae /app
USER falae
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
