FROM python:3.12-slim

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory to where GitHub mounts your action's code
WORKDIR /github/workspace

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to your script
ENTRYPOINT ["python", "main.py"]