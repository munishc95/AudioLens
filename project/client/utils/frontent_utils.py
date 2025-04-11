import requests
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv

backendendpoint = os.getenv("backendendpoint")
print(backendendpoint)

def display_audio_player(transcription, filename):
    """Display audio player with streaming audio"""
    audio_html = f"""
    <style>
        .audio-container {{
            background: #f0f2f6;a
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .audio-player {{
            width: 100%;
            margin-bottom: 20px;
        }}
        .transcription {{
            font-family: Arial, sans-serif;
            line-height: 1.8;
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background: white;
            border-radius: 5px;
        }}
    </style>
    <div class="audio-container">
        <audio id="audio" controls class="audio-player">
            <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
        </audio>
        <div class="transcription">
    """

    for line in transcription.strip().split("\n"):
        if line:
            try:
                timestamp_str = line[1:9]
                rest_of_line = line[11:]
                h, m, s = map(int, timestamp_str.split(":"))
                total_seconds = h * 3600 + m * 60 + s

                try:
                    speaker, text = rest_of_line.split(":", 1)
                    audio_html += f"""
                        <div>
                            <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
                            <span class="speaker-label">{speaker}:</span>
                            {text}
                        </div>"""
                except ValueError:
                    audio_html += f"""
                        <div>
                            <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
                            {rest_of_line}
                        </div>"""
            except:
                audio_html += f"<div>{line}</div>"

    audio_html += """
        </div>
    </div>
    <script>
        const audio = document.getElementById('audio');
        const timestamps = document.getElementsByClassName('timestamp');
        
        Array.from(timestamps).forEach(timestamp => {
            timestamp.addEventListener('click', function() {
                const timeInSeconds = parseFloat(this.getAttribute('data-time'));
                audio.currentTime = timeInSeconds;
                audio.play();
            });
        });
        
        audio.addEventListener('timeupdate', function() {
            const currentTime = audio.currentTime;
            Array.from(timestamps).forEach(timestamp => {
                const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
                if (Math.abs(currentTime - timeInSeconds) < 1) {
                    timestamp.style.color = '#ff7f0e';
                } else {
                    timestamp.style.color = '#1f77b4';
                }
            });
        });
    </script>
    """
    
    # Rest of the function remains same
    return audio_html



def display_chat_with_audio(transcription):
    """Display chat interface to ask questions about the audio"""
    st.subheader("Chat with Audio")
    
    # Initialize chat history for this feature
    if "qa_chat_history" not in st.session_state:
        st.session_state.qa_chat_history = []

    # Input for new question
    question = st.text_input(
        "Ask a question about the audio content:", 
        key="question_input_reset"
    )

    submit_button = st.button("Ask")

    if submit_button and question:
        with st.spinner("Generating answer..."):
            try:
                # Make request to backend API
                response = requests.post(
                    f"{backendendpoint}/ask",
                    json={
                        "transcription_text": transcription,
                        "question": question
                    }
                )
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "Sorry, I couldn't generate an answer.")
                    # Add to chat history
                    st.session_state.qa_chat_history.append((question, answer))
                    
                    # Clear input field by triggering a rerun
                    del st.session_state["question_input_reset"]
                    st.rerun()
                else:
                    st.error(f"Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for q, a in st.session_state.qa_chat_history:
            st.markdown(f"**Question:** {q}")
            st.markdown(f"**Answer:** {a}")
            st.markdown("---")
