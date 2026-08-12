FROM python:3.12-slim

WORKDIR /app

# hdbcli ships as a manylinux wheel — no build toolchain needed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Unbuffered so `docker compose logs -f loadgen` shows progress in real time
# rather than in 8 KB bursts.
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
