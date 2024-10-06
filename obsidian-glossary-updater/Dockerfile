# Use a lightweight Python image
FROM python:3.12-slim

# Install git to enable repository checkout
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy your action code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to your script
ENTRYPOINT ["python", "main.py"]