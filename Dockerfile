FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    uuid-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/CarAlgo:$PYTHONPATH

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pybind11

# Copy project files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]
