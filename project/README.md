# AudioLens

AudioLens is an AI-powered audio processing tool that transcribes, analyzes, and extracts key insights from audio recordings. Also supports hyperlinks. It leverages **Azure OpenAI**, **Azure Transcription Service**,  **Flask** and **Streamlit** for a seamless user experience.

---

## How to Run This Application

Follow the steps below to set up and run the **AudioLens** application.

---

## 1. Clone the Repository

Download the repository using the following command:

```bash
git clone https://github.com/nm1319/AudioLens.git
```

Navigate to the project folder:

```bash
cd AudioLens/project
```

---

## 2. Create and Activate a Virtual Environment

Run the following command to create a virtual environment:

```bash
python3 -m venv audiolens
```

Activate the virtual environment:

- **Linux/macOS**:  
  ```bash
  source audiolens/bin/activate
  ```
- **Windows (Command Prompt)**:  
  ```bash
  audiolens\Scripts\activate
  ```
- **Windows (PowerShell)**:  
  ```powershell
  audiolens\Scripts\Activate.ps1
  ```

---

## 3. Install FFmpeg (If Not Installed)

Ensure that **FFmpeg** and **FFprobe** are installed:

```bash
ffmpeg -version
ffprobe -version
```

If not installed, install them using:

- **Linux (Ubuntu/Debian-based)**:  
  ```bash
  sudo apt update && sudo apt install ffmpeg -y
  ```

- **macOS**: 
  Install using Homebrew (recommended):
  ```bash
  brew install ffmpeg
  ```

- **Windows**:  
  Option 1 : Download and install from [FFmpeg’s official website](https://ffmpeg.org/download.html).
              After downloading, you need to add FFmpeg to your system PATH:
            1. Extract the downloaded FFmpeg zip file to a folder (e.g., C:\ffmpeg).
            2. Copy the path to the bin folder inside the FFmpeg folder (e.g., C:\ffmpeg\bin).
            3. Open System Properties (right-click on This PC > Properties > Advanced system settings).
            4. Click on Environment Variables.
            5. Under System variables, find the Path variable, select it, and click Edit.
            6. In the Edit Environment Variable window, click New and paste the FFmpeg bin folder path (e.g., C:\ffmpeg\bin).
            7. Click OK to save and apply the changes.
            8. Restart your terminal or system for the changes to take effect.
            9. Now, run the following command in your terminal to check if FFmpeg is successfully added to your PATH:
              ```bash
                  ffmpeg -version
                  ```

  Option 2: Install via WSL (Windows Subsystem for Linux)
            If using WSL (Ubuntu on Windows), you can install FFmpeg like Linux:
            ```bash
            sudo apt update && sudo apt install ffmpeg -y
            ```
---

## 4. Install Dependencies

Navigate to the project root directory (where `requirements.txt` is located) and install dependencies:

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file in the **project root** directory and add the necessary details such as API keys, secrets, and tokens.

_(Ask the repo owner for the required credentials.)_

Example `.env` file:

```
# OpenAI API Configuration
openai_api_version=your_openai_api_version

# Azure OpenAI Configuration
azure_openai_endpoint=your_azure_openai_endpoint
azure_openai_api_key=your_azure_openai_api_key

# Azure Transcription Service Configuration
subscription_key=your_azure_transcription_subscription_key
region=your_azure_region

# Backend Endpoint for Communication
backendendpoint=http://127.0.0.1:5000
```

---

## 6. Run the Server

Navigate to the **server** folder:

```bash
cd server
```

Start the backend server:

```bash
python app.py
```

---

## 7. Run the Client

Open a **new terminal**, navigate to the **client** folder:

```bash
cd ../client
```

Run the Streamlit client application:

```bash
streamlit run app.py
```

---

## 8. Open the Application

Once both the server and client are running, open your browser and go to:

```
http://localhost:8501/
```

---

## 9. Test with Sample Audio Files

Download some `.mp3` or `.mp4` audio files to test the application. _(Ask the repo owner for sample files if needed.)_

---

Now, your **AudioLens** application is ready to use! 🚀









##  Deployment using Docker  

If you want to run AudioLens using **Docker**, follow these steps:  

### **1️⃣ Install Docker**  
- Download and install **Docker** from [Docker’s official website](https://docs.docker.com/get-docker/).
- Verify installation by running:
  ```bash
  docker --version
  ```

### 2️⃣ Pull the Docker Image
Run the following command to get the latest Docker image for AudioLens:
  ```bash
  docker pull parul1906/audiolens:latest
  ```

### 3️⃣ Set Up the Environment File (.env)
You need a .env file with the required API keys and backend settings. Do not add comments in the file keep it key value pair and values must not be in quotes.

Example `.env` file:

```
# OpenAI API Configuration
openai_api_version=your_openai_api_version

# Azure OpenAI Configuration
azure_openai_endpoint=your_azure_openai_endpoint
azure_openai_api_key=your_azure_openai_api_key

# Azure Transcription Service Configuration
subscription_key=your_azure_transcription_subscription_key
region=your_azure_region

# Backend Endpoint for Communication
backendendpoint=http://127.0.0.1:5000
FLASK_PORT=5000
```

---

### 4️⃣ Run the Docker Container
Now, start the container with the following command:
  ```bash
  docker run --env-file /path/to/.env -p 8501:8501 -p 5000:5000 --name audiolens_container parul1906/audiolens:latest
  ```
--env-file /path/to/.env → Loads environment variables.

-p 8501:8501 → Maps Streamlit UI port.

-p 5000:5000 → Maps Flask API port.

--name audiolens_container → Names the container.

### 5️⃣ Access the Application
Once the container is running:
Streamlit UI: Open http://localhost:8501.

6️⃣ Stopping & Removing the Container
Stop the container:

  ```bash
  docker stop audiolens_container
  ```
Remove the container:

  ```bash
  docker rm audiolens_container
  ```
