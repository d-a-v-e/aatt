FROM python:3.12-slim

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory for your action's code
WORKDIR /action

# Copy the action's code into the Docker image
COPY . /action

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to your script using the absolute path
ENTRYPOINT ["python", "/action/main.py"]