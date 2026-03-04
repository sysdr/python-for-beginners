# Use a lightweight official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY src /app/src

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Python script, then keep container alive for docker exec
CMD ["sh", "-c", "python src/main.py; python src/user_registration.py; exec tail -f /dev/null"]
