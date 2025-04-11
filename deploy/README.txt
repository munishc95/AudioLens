#navigate to the folder where Dockerfile is present

# Create the Docker Image
sudo docker build -t audiolenspoc .

# Flask backend is exposed on port 5010
# Streamlit UI is exposed on port 5000

# Run the Docker Image
sudo docker run -d -p 5010:5010 -p 5000:5000 --name my_audio_lens audiolenspoc

# Monitor the logs from the docker pod
sudo docker ps | grep 'audiolenspoc' | cut -d ' ' -f1 | xargs docker logs -f

# Stop the Docker container
sudo docker ps | grep 'audiolenspoc' | cut -d ' ' -f1 | xargs docker stop

# Remove the docker container
sudo docker rm my_audio_lens
