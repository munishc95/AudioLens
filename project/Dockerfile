# Step 1: Use an official Python base image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Install system dependencies including ffmpeg and supervisor
RUN apt-get update && apt-get install -y \
    ffmpeg \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy the requirements.txt to the container
COPY requirements.txt .

# Step 5: Install Python dependencies from requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the entire project directory into the container
COPY . /app/

# Step 7: Expose the ports (these will be dynamically configured at runtime)
EXPOSE 5000
EXPOSE 8501

# Step 8: Copy the Supervisor configuration file to the correct location
COPY ./supervisord.conf /etc/supervisor/conf.d/flask-streamlit.conf

# Step 9: Ensure environment variables are loaded from .env
ARG backendendpoint
ENV backendendpoint=${backendendpoint}

# Step 10: Command to run Supervisor, which will start Flask and Streamlit
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/flask-streamlit.conf"]
