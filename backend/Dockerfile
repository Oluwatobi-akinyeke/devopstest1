# Stage 1

FROM python:3.11-slim AS backend_builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y ca-certificates --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=backend_builder /install /usr/local

COPY main.py .

EXPOSE 8000 

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]