# Stage 1: Build dependencies
FROM python:3.11-slim AS backend_builder

WORKDIR /app

# Copy only requirements first (helps caching)
COPY requirements.txt .

# Install latest certificate files
RUN apt-get update && apt-get install -y ca-certificates --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into /install
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Final lightweight image
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy installed libs from builder stage
COPY --from=backend_builder /install /usr/local

# Copy FastAPI app
COPY main.py .

EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]