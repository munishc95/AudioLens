# Use the official Ubuntu base image
# FROM ubuntu:latest
FROM python:3.9-slim

# Install Python and pip
# RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get update && apt-get install -y python3-pip supervisor && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Expose the port that the app runs on
# EXPOSE 5000
# Define environment variable
# ENV FLASK_APP=app.py
# Run the application
# CMD ["flask", "run", "--host=0.0.0.0"]

EXPOSE 5000 5010

# Start supervisord to run both applications
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]