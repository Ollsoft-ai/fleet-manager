FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    uuid-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY CarAlgo ./CarAlgo
COPY app ./app
COPY run.py .

# Build and install the C++ extension
RUN cd CarAlgo && \
    make clean && \
    make all && \
    cp caralgo*.so /usr/local/lib/python3.11/site-packages/ && \
    cd ..

EXPOSE 80

# Add the current directory to PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["python", "run.py"]
