# How to run this application?
1. Download the git repo from https://github.com/nm1319/AudioLens.git
2. Create a virtual environment named audiolens (or whatever name you like)
    python3 -m venv audiolens
    source audiolens/bin/activate
3. Navigate to the code folder
x. sudo apt install ffmpeg
x. Check for the installed libraries by running the command:
ffmpeg -version
ffprobe -version
4. Install all libraries
    pip install -r requirements.txt
5. create a .env file and add details (secrets, tokens, keys etc) to it, ask from the repo owner.
6. In one terminal, run the command: streamlit run ui.py
7. In the other terminal, run the command: python3 app.py
8. Open the browser: http://localhost:8501/
9. Download some mp3/mp4 audio files, ask for samples from the repo owner.