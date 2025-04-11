import streamlit as st
import time
import requests
import base64
from PIL import Image
import io
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import re
load_dotenv()

backendendpoint = os.getenv("backendendpoint")

# outfilelocation = os.getenv("outfilelocation")

current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)
current_folder_path = f"{current_folder_path}/input/"


def encode_audio_to_base64(audio):
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    audio_bytes = buffer.getvalue()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return audio_base64

def extract_guest_names(summary):
    """Extract guest names from the summary"""
    guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
    guests = guest_pattern.findall(summary)
    guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
    return guests
    

def extract_companies(summary):
    """Extract companies from the summary"""
    companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
    companies = []
    print(companies_section)
    for line in companies_section.split('\n'):
        companies.append(line.strip())
    return companies

def display_qa_audio_player(transcription, filename):
    """Display audio player with streaming audio"""
    audio_html = f"""
    <style>
        .audio-container {{
            background: #f0f2f6;
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
        if line.startswith("Question") or line.startswith("Answer"):
            if line.startswith("Question"):
                question = True
            else:
                question = False     
            try:
                line = re.split(r":", line, 1)[1]
                try:
                    timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        if question:
                            rest_of_line = "Question: " + line[timestamp_match.end():]
                        else:
                            rest_of_line = "Answer: " + line[timestamp_match.end():]    
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
            except:
                pass        

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
    return audio_html


def get_analysis_sections(summary):
    """Extract different sections from stored summary"""
    return {
        "Summary": (
            summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()
            if "SUMMARY" in summary
            else "Audio too short to extract Summary"
        ),
        "Q&A": (
            summary.split("Question and Answer")[1]
            .split("LIST OF COMPANIES")[0]
            .strip()
            if "Question and Answer" in summary
            else "Audio too short to extract Q&A"
        ),
        "Companies": (
            summary.split("LIST OF COMPANIES")[1]
            .split("LIST OF ACTION ITEMS")[0]
            .strip()
            if "LIST OF COMPANIES" in summary
            else "Audio too short to extract list of Companies"
        ),
        "Sentiments": (
            summary.split("Sentiment Over Time")[1]
            .split("Acronyms and Full Forms")[0]
            .strip()
            if "Sentiment Over Time" in summary
            else "Audio too short to extract Sentiments"
        ),
        "Acronyms": (
            summary.split("Acronyms and Full Forms")[1].split("LIST OF ACTION ITEMS")[0].strip()
            .split("Action Items")[0]
            .strip()
            if "Acronyms and Full Forms" in summary
            else "Audio too short to extract Acronyms"
        ),
        "Action Items": (
            summary.split("Action Items")[1]
            if "Action Items" in summary
            else "Audio too short to extract Action Items"
        )
    }





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

def get_existing_files(folder_path):
    """Get list of existing wav files in input folder"""
    wav_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".wav"):
            wav_files.append(file)
    return wav_files



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



def main():
    st.title("Meeting Transcription and Analysis")
    
    st.markdown(
        """
        <style>
        .stCheckbox label {
            white-space: nowrap;
            min-width: auto;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session states
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar setup
    st.sidebar.title("AudioLens")
    st.sidebar.write(f":User  User")

    # Display chat history
    st.sidebar.subheader("Previous Uploads")
    for i, (file_name, transcription, summary) in enumerate(
        st.session_state.chat_history
    ):
        if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
            st.session_state.transcription = transcription
            st.session_state.summary = summary
            st.session_state.transcription_complete = True

    input_type = st.radio(
        "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
    )

    selected_file = None
    uploaded_file = None
    youtube_link = None

    if input_type == "Upload new file":
        uploaded_file = st.file_uploader(
            "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
        )
        selected_file = uploaded_file

    elif input_type == "Select existing file":
        existing_files = get_existing_files(current_folder_path)
        if existing_files:
            selected_filename = st.selectbox(
                "Select an existing recording", existing_files
            )
            if selected_filename:
                selected_file = f"{current_folder_path}/{selected_filename}"
                st.session_state.selected_filename = selected_filename

                if st.button("Process Selected File"):
                    with open(selected_file, "rb") as f:
                        uploaded_file = io.BytesIO(f.read())
        else:
            st.warning("No existing .wav files found in input folder")

    elif input_type == "YouTube Video Link":
        youtube_link = st.text_input("Enter YouTube Video URL")

        if st.button("Download and Process"):
            if youtube_link:
                with st.spinner("Downloading..."):
                    progress_bar = st.progress(0)

                    # Simulate progress while waiting for the response
                    for percent_complete in range(50):  # Halfway while waiting
                        time.sleep(0.01)
                        progress_bar.progress(percent_complete + 1)

                    response = requests.post(
                        f"{backendendpoint}/download_youtube_audio",
                        json={"url": youtube_link}
                    )

                    for percent_complete in range(50, 100):  # Complete progress bar
                        time.sleep(0.01)
                        progress_bar.progress(percent_complete + 1)

                if response.status_code == 200:
                    # Store the downloaded file path in session state
                    audio_file_path = response.json().get("audio_file_path")
                    print(audio_file_path)

                    # Normalize the path to ensure correct backslashes
                    audio_file_path = os.path.normpath(audio_file_path)
                    st.session_state.selected_filename = audio_file_path
                    st.session_state.transcription_complete = False
                    st.success("Audio downloaded successfully!")

                    # Use the normalized file path to access the file
                    selected_filename = os.path.basename(audio_file_path)  # Get just the file name
                    selected_file = os.path.join(current_folder_path, selected_filename)

                    # Check if file exists before reading
                    if os.path.exists(selected_file):
                        with open(selected_file, "rb") as f:
                            uploaded_file = io.BytesIO(f.read())
                    else:
                        st.error(f"File not found: {selected_file}")
                else:
                    st.error("Failed to download audio from YouTube.")

    if selected_file is not None and uploaded_file is not None:
        # Process file
        with st.spinner("Processing..."):
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)

        # Get API response if not already processed
        if "transcription" not in st.session_state:
            with st.spinner("Generating Transcript"):
                try:
                    if input_type == "Upload new file":
                        files = {"file": selected_file}
                    else:
                        files = {"file": open(selected_file, "rb")}

                    response = requests.post(
                        f"{backendendpoint}/transcribe", files=files
                    )
                    response_data = response.json()
                    print(response_data)
                    # Store response data in session state
                    st.session_state.transcription = response_data["transcription"]
                    st.session_state.summary = response_data["summary"]
                    st.session_state.visualizations = response_data.get(
                        "visualizations", {}
                    )
                    st.session_state.transcription_complete = True

                    # Update chat history
                    filename = (
                        selected_file.name
                        if input_type == "Upload new file"
                        else os.path.basename(selected_file)
                    )
                    st.session_state.chat_history.append(
                        (
                            filename,
                            st.session_state.transcription,
                            st.session_state.summary,
                        )
                    )

                    if input_type == "Select existing file":
                        files["file"].close()

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.write(
                        "Please try again or contact support if the problem persists."
                    )

    if st.session_state.get("transcription_complete", False):
        
        sections = get_analysis_sections(st.session_state.summary)
        col1, col2 = st.columns([6,1])
        with col2:
            if st.button("Create PDF", type="primary"):
                # Prepare selected sections
                selected_sections = {
                "Names & Entities": {
                    "Guest Names": "\n".join(st.session_state.guest_names),
                    "Companies": "\n".join(st.session_state.companies)
                    },
                    "Summary": sections["Summary"],
                    "QnA": sections["Q&A"],
                    "Sentiments": sections["Sentiments"],
                    "Action Items": sections["Action Items"],
                    "Acronyms": sections["Acronyms"]
                }
                
                visualization_images = []
                if "visualizations":
                    visualization_images = [
                        st.session_state.visualizations['turn_count_plot'], 
                        st.session_state.visualizations['word_count_plot']
                    ]

                # Send request to backend
                with st.spinner("Generating PDF..."):
                    try:
                        response = requests.post(
                            f"{backendendpoint}/generate_pdf",
                            json={
                                "sections": selected_sections,
                                "transcription": st.session_state.transcription,
                                "visualizations": visualization_images
                            }
                        )
                        if response.status_code == 200:
                            # Trigger download
                            st.download_button(
                                "Download PDF",
                                response.content,
                                file_name="meeting_summary.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error("Failed to generate PDF")
                    except Exception as e:
                        print(e)
                        st.error(f"An error occurred: {str(e)}")    

    # Display analysis if we have data
    if st.session_state.get("transcription_complete", False):
        sections = get_analysis_sections(st.session_state.summary)
        st.session_state.guest_names = extract_guest_names(st.session_state.summary)
        st.session_state.companies = extract_companies(st.session_state.summary)
        tabs = ["Names & Entities"]
        # if summarization:
        tabs.append("Summary")
        # if qa:
        tabs.append("Q&A")
        # if sentiments:
        tabs.append("Sentiments")
        # if action_items:
        tabs.append("Action Items")
        # if acronyms:
        tabs.append("Acronyms")
        # if visualizations:
        tabs.append("Visualizations")
        # Add the new Chat with Audio tab
        tabs.append("Chat with Audio")   
        tabs.append("Transcription")

        if tabs:
            tab_objects = st.tabs(tabs)
            with tab_objects[0]:
                st.subheader("Guest Names")
                for name in st.session_state.guest_names:
                    st.write(name)
                
                st.subheader("Companies")
                for company in st.session_state.companies:
                    st.write(company)
            tab_index = 1

            # if summarization:
            with tab_objects[tab_index]:
                st.subheader("Summary")
                st.markdown(sections["Summary"])
            tab_index += 1
            # if qa:
            with tab_objects[tab_index]:
                if uploaded_file:
                    try:
                        filename_qna = uploaded_file.name
                        if filename_qna.endswith(".mp4"):
                            filename_qna = filename_qna.replace(".mp4", ".wav")
                        print(filename_qna)
                        st.markdown("### Q&A Audio Player")
                        audio_html = display_audio_player(
                        sections["Q&A"], 
                            filename_qna
                        )
                        components.html(audio_html, height=700)
                    except AttributeError:
                        filename_qna = selected_filename
                        st.markdown("### Q&A Audio Player")
                        audio_html = display_audio_player(
                        sections["Q&A"], 
                            filename_qna
                        )
                        components.html(audio_html, height=700)

            tab_index += 1
            with tab_objects[tab_index]:
                st.subheader("Sentiments")
                st.markdown(sections["Sentiments"])
            tab_index += 1
            # if action_items:
            with tab_objects[tab_index]:
                st.subheader("Action Items")
                st.markdown(sections["Action Items"])
                tab_index += 1
            # if acronyms:
            with tab_objects[tab_index]:
                st.subheader("Acronyms")
                st.markdown(sections["Acronyms"])
            tab_index += 1

            # Display visualizations
            with tab_objects[tab_index]:
                st.subheader("Visualizations")
                col1, col2 = st.columns(2)

                with col1:
                    st.image(
                        f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
                        caption="Speaker Turn Distribution",
                        use_container_width=True,
                    )

                with col2:
                    st.image(
                        f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
                        caption="Speaker Word Count Distribution",
                        use_container_width=True,
                    )
            tab_index += 1

            # Add the Chat with Audio tab functionality
            with tab_objects[tab_index]:
                display_chat_with_audio(st.session_state.transcription)
            tab_index += 1

            with tab_objects[-1]:
                if uploaded_file:
                    try:
                        filename = uploaded_file.name
                        if filename.endswith(".mp4"):
                            filename = filename.replace(".mp4", ".wav")
                        st.markdown("### Audio Player and Interactive Transcription")
                        audio_html = display_audio_player(
                            st.session_state.transcription, 
                            filename
                        )
                        components.html(audio_html, height=700)
                    except AttributeError:
                        filename = selected_filename
                        if filename.endswith(".mp4"):
                            filename = filename.replace(".mp4", ".wav")
                        st.markdown("### Audio Player and Interactive Transcription")
                        audio_html = display_audio_player(
                            st.session_state.transcription, 
                            filename
                        )
                        components.html(audio_html, height=700)


if __name__ == "__main__":
    main()









#without pdf and some places problems
# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Acronyms": "None identified in the conversation.",
#         "Action Items": "Audio too short to extract Action Items"
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].split("ACTION ITEMS")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User   User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 st.markdown(sections["Q&A"])

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 st.markdown(sections["Action Items"])

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 st.markdown(sections["Acronyms"])

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 col1, col2 = st.columns(2)

#                 with col1:
#                     st.image(
#                         f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                         caption="Speaker Turn Distribution",
#                         use_container_width=True,
#                     )

#                 with col2:
#                     st.image(
#                         f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                         caption="Speaker Word Count Distribution",
#                         use_container_width=True,
#                     )

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()



#Improved code
# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(t imestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Acronyms": "None identified in the conversation.",
#         "Action Items": "Audio too short to extract Action Items"
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].split("ACTION ITEMS")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     return audio_html

# def get_existing_files(folder_path):
#     #"""Get list of existing wav files in input folder ```python
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User    User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st .session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 col1, col2 = st.columns(2)

#                 with col1:
#                     st.image(
#                         f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                         caption="Speaker Turn Distribution",
#                         use_container_width=True,
#                     )

#                 with col2:
#                     st.image(
#                         f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                         caption="Speaker Word Count Distribution",
#                         use_container_width=True,
#                     )

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

#         # PDF Generation
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations['turn_count_plot'], 
#                         st.session_state.visualizations['word_count_plot']
#                     ]

#                 # Send request to backend for PDF generation
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")    

# if __name__ == "__main__":
#     main()























#more better
# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     < ```python
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Acronyms": "None identified in the conversation.",
#         "Action Items": "Audio too short to extract Action Items"
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].split("ACTION ITEMS")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const current _time = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User      User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         # Create PDF button above tabs
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations.get('turn_count_plot'), 
#                         st.session_state.visualizations.get('word_count_plot')
#                     ]

#                 # Send request to backend for PDF generation
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")    

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 if "visualizations" in st.session_state:
#                     if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                             caption="Speaker Turn Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Turn count plot is not available.")

#                     if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                             caption="Speaker Word Count Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Word count plot is not available.")
#                 else:
#                     st.warning("No visualizations available.")

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()

















# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Acronyms": "None identified in the conversation.",
#         "Action Items": "Audio too short to extract Action Items"
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].split("ACTION ITEMS")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User      User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         # Create PDF button above tabs
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations.get('turn_count_plot'), 
#                         st.session_state.visualizations.get('word_count_plot')
#                     ]

#                 # Send request to backend for PDF generation
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")    

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 if "visualizations" in st.session_state:
#                     if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                             caption="Speaker Turn Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Turn count plot is not available.")

#                     if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                             caption="Speaker Word Count Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Word count plot is not available.")
#                 else:
#                     st.warning("No visualizations available.")

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()





















# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Action Items": "Audio too short to extract Action Items",
#         "Acronyms": "None identified in the conversation."
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User      User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         # Create PDF button above tabs
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations.get('turn_count_plot'), 
#                         st.session_state.visualizations.get('word_count_plot')
#                     ]

#                 # Send request to backend for PDF generation
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")    

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 if "visualizations" in st.session_state:
#                     if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                             caption="Speaker Turn Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Turn count plot is not available.")

#                     if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                             caption="Speaker Word Count Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Word count plot is not available.")
#                 else:
#                     st.warning("No visualizations available.")

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()




















# import streamlit as st
# import time
# import requests
# import base64
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     try:
#         companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#         companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#         return companies
#     except IndexError:
#         return ["No specific companies were mentioned."]

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio and Q&A text"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             try:
#                 timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                 if timestamp_match:
#                     timestamp_str = timestamp_match.group(1)
#                     h, m, s = map(int, timestamp_str.split(":"))
#                     total_seconds = h * 3600 + m * 60 + s

#                     rest_of_line = line[timestamp_match.end():].strip()
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     sections = {
#         "Summary": "Audio too short to extract Summary",
#         "Q&A": "Audio too short to extract Q&A",
#         "Companies": "No specific companies were mentioned.",
#         "Sentiments": "Audio too short to extract Sentiments",
#         "Action Items": "Audio too short to extract Action Items",
#         "Acronyms": "None identified in the conversation."
#     }

#     if "SUMMARY" in summary:
#         sections["Summary"] = summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()

#     if "Question and Answer" in summary:
#         sections["Q&A"] = summary.split("Question and Answer")[1].split("LIST OF COMPANIES")[0].strip()

#     if "LIST OF COMPANIES" in summary:
#         sections["Companies"] = extract_companies(summary)

#     if "Sentiment Over Time" in summary:
#         sections["Sentiments"] = summary.split("Sentiment Over Time")[1].split("Acronyms and Full Forms")[0].strip()

#     if "ACTION ITEMS" in summary:
#         sections["Action Items"] = summary.split("ACTION ITEMS")[1].split("Acronyms and Full Forms")[0].strip()

#     if "Acronyms and Full Forms" in summary:
#         sections["Acronyms"] = summary.split("Acronyms and Full Forms")[1].strip()

#     return sections

# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     # Initialize session states
#     if "transcription" not in st.session_state:
#         st.session_state.transcription = ""
#     if "summary" not in st.session_state:
#         st.session_state.summary = ""
#     if "transcription_complete" not in st.session_state:
#         st.session_state.transcription_complete = False
#     if "visualizations" not in st.session_state:
#         st.session_state.visualizations = {}
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User      User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         # Create PDF button above tabs
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations.get('turn_count_plot'), 
#                         st.session_state.visualizations.get('word_count_plot')
#                     ]

#                 # Send request to backend for PDF generation
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")    

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)
                
#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)
           
#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 if "visualizations" in st.session_state:
#                     if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                             caption="Speaker Turn Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Turn count plot is not available.")

#                     if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                             caption="Speaker Word Count Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Word count plot is not available.")
#                 else:
#                     st.warning("No visualizations available.")

#             with tab_objects[7]:
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown(" ### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()







































# import streamlit as st
# import time
# import requests
# import base64
# from PIL import Image
# import io
# import streamlit.components.v1 as components
# from dotenv import load_dotenv
# import os
# import re
# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")

# # outfilelocation = os.getenv("outfilelocation")

# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"


# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     """Extract guest names from the summary"""
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests
    

# def extract_companies(summary):
#     """Extract companies from the summary"""
#     companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#     companies = []
#     print(companies_section)
#     for line in companies_section.split('\n'):
#         companies.append(line.strip())
#     return companies

# def display_qa_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             if line.startswith("Question"):
#                 question = True
#             else:
#                 question = False     
#             try:
#                 line = re.split(r":", line, 1)[1]
#                 try:
#                     timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                     if timestamp_match:
#                         timestamp_str = timestamp_match.group(1)
#                         if question:
#                             rest_of_line = "Question: " + line[timestamp_match.end():]
#                         else:
#                             rest_of_line = "Answer: " + line[timestamp_match.end():]    
#                         h, m, s = map(int, timestamp_str.split(":"))
#                         total_seconds = h * 3600 + m * 60 + s

#                         try:
#                             speaker, text = rest_of_line.split(":", 1)
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         <span class="speaker-label">{speaker}:</span>
#                                         {text}
#                                     </div>"""
#                         except ValueError:
#                             audio_html += f"""
#                                     <div>
#                                         <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                                         {rest_of_line}
#                                     </div>"""
#                 except:
#                     audio_html += f"<div>{line}</div>"
#             except:
#                 pass        

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html


# def get_analysis_sections(summary):
#     """Extract different sections from stored summary"""
#     return {
#         "Summary": (
#             summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()
#             if "SUMMARY" in summary
#             else "Audio too short to extract Summary"
#         ),
#         "Q&A": (
#             summary.split("Question and Answer")[1]
#             .split("LIST OF COMPANIES")[0]
#             .strip()
#             if "Question and Answer" in summary
#             else "Audio too short to extract Q&A"
#         ),
#         "Companies": (
#             summary.split("LIST OF COMPANIES")[1]
#             .split("LIST OF ACTION ITEMS")[0]
#             .strip()
#             if "LIST OF COMPANIES" in summary
#             else "Audio too short to extract list of Companies"
#         ),
#         "Sentiments": (
#             summary.split("Sentiment Over Time")[1]
#             .split("Acronyms and Full Forms")[0]
#             .strip()
#             if "Sentiment Over Time" in summary
#             else "Audio too short to extract Sentiments"
#         ),
#         "Acronyms": (
#             summary.split("Acronyms and Full Forms")[1].split("LIST OF ACTION ITEMS")[0].strip()
#             .split("Action Items")[0]
#             .strip()
#             if "Acronyms and Full Forms" in summary
#             else "Audio too short to extract Acronyms"
#         ),
#         "Action Items": (
#             summary.split("Action Items")[1]
#             if "Action Items" in summary
#             else "Audio too short to extract Action Items"
#         )
#     }





# def display_audio_player(transcription, filename):
#     """Display audio player with streaming audio"""
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;a
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
    
#     # Rest of the function remains same
#     return audio_html

# def get_existing_files(folder_path):
#     """Get list of existing wav files in input folder"""
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files


# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Initialize session states
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     # Sidebar setup
#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User  User")

#     # Display chat history
#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(
#         st.session_state.chat_history
#     ):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     # Simulate progress while waiting for the response
#                     for percent_complete in range(50):  # Halfway while waiting
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):  # Complete progress bar
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     # Store the downloaded file path in session state
#                     audio_file_path = response.json().get("audio_file_path")
#                     print(audio_file_path)

#                     # Normalize the path to ensure correct backslashes
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")
#                     #st.write(f"Downloaded audio file path: {audio_file_path}")

#                     # ✅ Use the normalized file path to access the file
#                     selected_filename = os.path.basename(audio_file_path)  # Get just the file name
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     # Check if file exists before reading
#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         # Process file
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         # Get API response if not already processed
#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     print(response_data)
#                     # Store response data in session state
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     # Update chat history
#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )



#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 # Prepare selected sections
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 # Prepare visualizations
#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations['turn_count_plot'],
#                         st.session_state.visualizations['word_count_plot']
#                     ]

#                 # Send request to backend
#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             # Trigger download
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         print(e)
#                         st.error(f"An error occurred: {str(e)}")

#         # Display analysis if we have data
#         if st.session_state.get("transcription_complete", False):
#             sections = get_analysis_sections(st.session_state.summary)
#             st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#             st.session_state.companies = extract_companies(st.session_state.summary)
#             tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#             if tabs:
#                 tab_objects = st.tabs(tabs)
#                 with tab_objects[0]:
#                     st.subheader("Guest Names")
#                     for name in st.session_state.guest_names:
#                         st.write(name)

#                     st.subheader("Companies")
#                     for company in st.session_state.companies:
#                         st.write(company)

#                 with tab_objects[1]:
#                     st.subheader("Summary")
#                     st.markdown(sections["Summary"])

#                 with tab_objects[2]:
#                     st.subheader("Q&A")
#                     st.markdown(sections["Q&A"])
#                     if uploaded_file:
#                         try:
#                             filename_qna = uploaded_file.name
#                             if filename_qna.endswith(".mp4"):
#                                 filename_qna = filename_qna.replace(".mp4", ".wav")
#                             st.markdown("### Q&A Audio Player")
#                             audio_html = display_audio_player(
#                                 sections["Q&A"], 
#                                 filename_qna
#                             )
#                             components.html(audio_html, height=700)
#                         except AttributeError:
#                             filename_qna = st.session_state.selected_filename
#                             st.markdown("### Q&A Audio Player")
#                             audio_html = display_audio_player(
#                                 sections["Q&A"], 
#                                 filename_qna
#                             )
#                             components.html(audio_html, height=700)

#                 with tab_objects[3]:
#                     st.subheader("Sentiments")
#                     st.markdown(sections["Sentiments"])

#                 with tab_objects[4]:
#                     st.subheader("Action Items")
#                     action_items = sections["Action Items"].strip()
#                     if action_items == "Audio too short to extract Action Items":
#                         st.write("No action items were extracted.")
#                     else:
#                         st.markdown(action_items)

#                 with tab_objects[5]:
#                     st.subheader("Acronyms")
#                     acronyms = sections["Acronyms"].strip()
#                     if acronyms == "None identified in the conversation.":
#                         st.write("No acronyms were mentioned in the conversation.")
#                     else:
#                         st.markdown(acronyms)

#                 with tab_objects[6]:
#                     st.subheader("Visualizations")
#                     if "visualizations" in st.session_state:
#                         if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                             st.image(
#                                 f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                                 caption="Speaker Turn Distribution",
#                                 use_container_width=True,
#                             )
#                         else:
#                             st.warning("Turn count plot is not available.")

#                         if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                             st.image(
#                                 f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                                 caption="Speaker Word Count Distribution",
#                                 use_container_width=True,
#                             )
#                         else:
#                             st.warning("Word count plot is not available.")
#                     else:
#                         st.warning("No visualizations available.")

#                 with tab_objects[7]:
#                     st.subheader("Transcription")
#                     st.markdown(st.session_state.transcription)
#                     if uploaded_file:
#                         try:
#                             filename = uploaded_file.name
#                             if filename.endswith(".mp4"):
#                                 filename = filename.replace(".mp4", ".wav")
#                             st.markdown("### Audio Player and Interactive Transcription")
#                             audio_html = display_audio_player(
#                                 st.session_state.transcription, 
#                                 filename
#                             )
#                             components.html(audio_html, height=700)
#                         except AttributeError:
#                             filename = st.session_state.selected_filename
#                             if filename.endswith(".mp4"):
#                                 filename = filename.replace(".mp4", ".wav")
#                             st.markdown("### Audio Player and Interactive Transcription")
#                             audio_html = display_audio_player(
#                                 st.session_state.transcription, 
#                                 filename
#                             )
#                             components.html(audio_html, height=700)


# if __name__ == "__main__":
#     main()

























# import streamlit as st
# import requests
# import io
# import os
# import re
# import time
# import streamlit.components.v1 as components
# from dotenv import load_dotenv

# load_dotenv()

# backendendpoint = os.getenv("backendendpoint")
# current_file_path = os.path.abspath(__file__)
# current_folder_path = os.path.dirname(current_file_path)
# current_folder_path = f"{current_folder_path}/input/"

# def encode_audio_to_base64(audio):
#     buffer = io.BytesIO()
#     audio.export(buffer, format="wav")
#     audio_bytes = buffer.getvalue()
#     audio_base64 = base64.b64encode(audio_bytes).decode()
#     return audio_base64

# def extract_guest_names(summary):
#     guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
#     guests = guest_pattern.findall(summary)
#     guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
#     return guests

# def extract_companies(summary):
#     companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
#     companies = [line.strip() for line in companies_section.split('\n') if line.strip()]
#     return companies

# def get_analysis_sections(summary):
#     return {
#         "Summary": (
#             summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()
#             if "SUMMARY" in summary
#             else "Audio too short to extract Summary"
#         ),
#         "Q&A": (
#             summary.split("Question and Answer")[1]
#             .split("LIST OF COMPANIES")[0]
#             .strip()
#             if "Question and Answer" in summary
#             else "Audio too short to extract Q&A"
#         ),
#         "Companies": (
#             summary.split("LIST OF COMPANIES")[1]
#             .split("Sentiment Over Time")[0]
#             .strip()
#             if "LIST OF COMPANIES" in summary
#             else "Audio too short to extract list of Companies"
#         ),
#         "Sentiments": (
#             summary.split("Sentiment Over Time")[1]
#             .split("Acronyms and Full Forms")[0]
#             .strip()
#             if "Sentiment Over Time" in summary
#             else "Audio too short to extract Sentiments"
#         ),
#         "Acronyms": (
#             summary.split("Acronyms and Full Forms")[1]
#             .split("ACTION ITEMS")[0]
#             .strip()
#             if "Acronyms and Full Forms" in summary
#             else "Audio too short to extract Acronyms"
#         ),
#         "Action Items": (
#             summary.split("ACTION ITEMS")[1]
#             .strip()
#             if "ACTION ITEMS" in summary
#             else "Audio too short to extract Action Items"
#         )
#     }

# def display_qa_audio_player(transcription, filename):
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line.startswith("Question") or line.startswith("Answer"):
#             try:
#                 timestamp_match = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", line)
#                 if timestamp_match:
#                     timestamp_str = timestamp_match.group(1)
#                     h, m, s = map(int, timestamp_str.split(":"))
#                     total_seconds = h * 3600 + m * 60 + s

#                     rest_of_line = line[timestamp_match.end():].strip()
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def display_audio_player(transcription, filename):
#     audio_html = f"""
#     <style>
#         .audio-container {{
#             background: #f0f2f6;
#             padding: 20px;
#             border-radius: 10px;
#             margin-bottom: 20px;
#         }}
#         .audio-player {{
#             width: 100%;
#             margin-bottom: 20px;
#         }}
#         .transcription {{
#             font-family: Arial, sans-serif;
#             line-height: 1.8;
#             max-height: 400px;
#             overflow-y: auto;
#             padding: 15px;
#             background: white;
#             border-radius: 5px;
#         }}
#     </style>
#     <div class="audio-container">
#         <audio id="audio" controls class="audio-player">
#             <source src="{backendendpoint}/stream-audio/{filename}" type="audio/wav">
#         </audio>
#         <div class="transcription">
#     """

#     for line in transcription.strip().split("\n"):
#         if line:
#             try:
#                 timestamp_str = line[1:9]
#                 rest_of_line = line[11:]
#                 h, m, s = map(int, timestamp_str.split(":"))
#                 total_seconds = h * 3600 + m * 60 + s

#                 try:
#                     speaker, text = rest_of_line.split(":", 1)
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             <span class="speaker-label">{speaker}:</span>
#                             {text}
#                         </div>"""
#                 except ValueError:
#                     audio_html += f"""
#                         <div>
#                             <span class="timestamp" data-time="{total_seconds}">[{timestamp_str}]</span>
#                             {rest_of_line}
#                         </div>"""
#             except:
#                 audio_html += f"<div>{line}</div>"

#     audio_html += """
#         </div>
#     </div>
#     <script>
#         const audio = document.getElementById('audio');
#         const timestamps = document.getElementsByClassName('timestamp');
        
#         Array.from(timestamps).forEach(timestamp => {
#             timestamp.addEventListener('click', function() {
#                 const timeInSeconds = parseFloat(this.getAttribute('data-time'));
#                 audio.currentTime = timeInSeconds;
#                 audio.play();
#             });
#         });
        
#         audio.addEventListener('timeupdate', function() {
#             const currentTime = audio.currentTime;
#             Array.from(timestamps).forEach(timestamp => {
#                 const timeInSeconds = parseFloat(timestamp.getAttribute('data-time'));
#                 if (Math.abs(currentTime - timeInSeconds) < 1) {
#                     timestamp.style.color = '#ff7f0e';
#                 } else {
#                     timestamp.style.color = '#1f77b4';
#                 }
#             });
#         });
#     </script>
#     """
#     return audio_html

# def get_existing_files(folder_path):
#     wav_files = []
#     for file in os.listdir(folder_path):
#         if file.endswith(".wav"):
#             wav_files.append(file)
#     return wav_files

# def main():
#     st.title("Meeting Transcription and Analysis")
    
#     st.markdown(
#         """
#         <style>
#         .stCheckbox label {
#             white-space: nowrap;
#             min-width: auto;
#         }
#         </style>
#     """,
#         unsafe_allow_html=True,
#     )

#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     st.sidebar.title("AudioLens")
#     st.sidebar.write(f":User      User")

#     st.sidebar.subheader("Previous Uploads")
#     for i, (file_name, transcription, summary) in enumerate(st.session_state.chat_history):
#         if st.sidebar.button(f"View {file_name}", key=f"view_{i}"):
#             st.session_state.transcription = transcription
#             st.session_state.summary = summary
#             st.session_state.transcription_complete = True

#     input_type = st.radio(
#         "Choose input source", ["Upload new file", "Select existing file", "YouTube Video Link"]
#     )

#     selected_file = None
#     uploaded_file = None
#     youtube_link = None

#     if input_type == "Upload new file":
#         uploaded_file = st.file_uploader(
#             "Upload a recorded meeting", type=["wav", "mp3", "mp4"]
#         )
#         selected_file = uploaded_file

#     elif input_type == "Select existing file":
#         existing_files = get_existing_files(current_folder_path)
#         if existing_files:
#             selected_filename = st.selectbox(
#                 "Select an existing recording", existing_files
#             )
#             if selected_filename:
#                 selected_file = f"{current_folder_path}/{selected_filename}"
#                 st.session_state.selected_filename = selected_filename

#                 if st.button("Process Selected File"):
#                     with open(selected_file, "rb") as f:
#                         uploaded_file = io.BytesIO(f.read())
#         else:
#             st.warning("No existing .wav files found in input folder")

#     elif input_type == "YouTube Video Link":
#         youtube_link = st.text_input("Enter YouTube Video URL")

#         if st.button("Download and Process"):
#             if youtube_link:
#                 with st.spinner("Downloading..."):
#                     progress_bar = st.progress(0)

#                     for percent_complete in range(50):
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                     response = requests.post(
#                         f"{backendendpoint}/download_youtube_audio",
#                         json={"url": youtube_link}
#                     )

#                     for percent_complete in range(50, 100):
#                         time.sleep(0.01)
#                         progress_bar.progress(percent_complete + 1)

#                 if response.status_code == 200:
#                     audio_file_path = response.json().get("audio_file_path")
#                     audio_file_path = os.path.normpath(audio_file_path)
#                     st.session_state.selected_filename = audio_file_path
#                     st.session_state.transcription_complete = False
#                     st.success("Audio downloaded successfully!")

#                     selected_filename = os.path.basename(audio_file_path)
#                     selected_file = os.path.join(current_folder_path, selected_filename)

#                     if os.path.exists(selected_file):
#                         with open(selected_file, "rb") as f:
#                             uploaded_file = io.BytesIO(f.read())
#                     else:
#                         st.error(f"File not found: {selected_file}")
#                 else:
#                     st.error("Failed to download audio from YouTube.")

#     if selected_file is not None and uploaded_file is not None:
#         with st.spinner("Processing..."):
#             progress_bar = st.progress(0)
#             for percent_complete in range(100):
#                 time.sleep(0.01)
#                 progress_bar.progress(percent_complete + 1)

#         if "transcription" not in st.session_state:
#             with st.spinner("Generating Transcript"):
#                 try:
#                     if input_type == "Upload new file":
#                         files = {"file": selected_file}
#                     else:
#                         files = {"file": open(selected_file, "rb")}

#                     response = requests.post(
#                         f"{backendendpoint}/transcribe", files=files
#                     )
#                     response_data = response.json()
#                     st.session_state.transcription = response_data["transcription"]
#                     st.session_state.summary = response_data["summary"]
#                     st.session_state.visualizations = response_data.get(
#                         "visualizations", {}
#                     )
#                     st.session_state.transcription_complete = True

#                     filename = (
#                         selected_file.name
#                         if input_type == "Upload new file"
#                         else os.path.basename(selected_file)
#                     )
#                     st.session_state.chat_history.append(
#                         (
#                             filename,
#                             st.session_state.transcription,
#                             st.session_state.summary,
#                         )
#                     )

#                     if input_type == "Select existing file":
#                         files["file"].close()

#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#                     st.write(
#                         "Please try again or contact support if the problem persists."
#                     )

#     if st.session_state.get("transcription_complete", False):
#         sections = get_analysis_sections(st.session_state.summary)
#         st.session_state.guest_names = extract_guest_names(st.session_state.summary)
#         st.session_state.companies = extract_companies(st.session_state.summary)
#         tabs = ["Names & Entities", "Summary", "Q&A", "Sentiments", "Action Items", "Acronyms", "Visualizations", "Transcription"]

#         col1, col2 = st.columns([6, 1])
#         with col2:
#             if st.button("Create PDF", type="primary"):
#                 selected_sections = {
#                     "Names & Entities": {
#                         "Guest Names": "\n".join(st.session_state.guest_names),
#                         "Companies": "\n".join(st.session_state.companies)
#                     },
#                     "Summary": sections["Summary"],
#                     "QnA": sections["Q&A"],
#                     "Sentiments": sections["Sentiments"],
#                     "Action Items": sections["Action Items"],
#                     "Acronyms": sections["Acronyms"]
#                 }

#                 visualization_images = []
#                 if "visualizations" in st.session_state:
#                     visualization_images = [
#                         st.session_state.visualizations['turn_count_plot'],
#                         st.session_state.visualizations['word_count_plot']
#                     ]

#                 with st.spinner("Generating PDF..."):
#                     try:
#                         response = requests.post(
#                             f"{backendendpoint}/generate_pdf",
#                             json={
#                                 "sections": selected_sections,
#                                 "transcription": st.session_state.transcription,
#                                 "visualizations": visualization_images
#                             }
#                         )
#                         if response.status_code == 200:
#                             st.download_button(
#                                 "Download PDF",
#                                 response.content,
#                                 file_name="meeting_summary.pdf",
#                                 mime="application/pdf"
#                             )
#                         else:
#                             st.error("Failed to generate PDF")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")

#         if tabs:
#             tab_objects = st.tabs(tabs)
#             with tab_objects[0]:
#                 st.subheader("Guest Names")
#                 for name in st.session_state.guest_names:
#                     st.write(name)

#                 st.subheader("Companies")
#                 for company in st.session_state.companies:
#                     st.write(company)

#             with tab_objects[1]:
#                 st.subheader("Summary")
#                 st.markdown(sections["Summary"])

#             with tab_objects[2]:
#                 st.subheader("Q&A")
#                 if uploaded_file:
#                     try:
#                         filename_qna = uploaded_file.name
#                         if filename_qna.endswith(".mp4"):
#                             filename_qna = filename_qna.replace(".mp4", ".wav")
#                         st.markdown("### Q&A Audio Player")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename_qna = st.session_state.selected_filename
#                         st.markdown("### Q&A Audio Player")
#                         audio_html = display_qa_audio_player(
#                             sections["Q&A"], 
#                             filename_qna
#                         )
#                         components.html(audio_html, height=700)

#             with tab_objects[3]:
#                 st.subheader("Sentiments")
#                 st.markdown(sections["Sentiments"])

#             with tab_objects[4]:
#                 st.subheader("Action Items")
#                 action_items = sections["Action Items"].strip()
#                 if action_items == "Audio too short to extract Action Items":
#                     st.write("No action items were extracted.")
#                 else:
#                     st.markdown(action_items)

#             with tab_objects[5]:
#                 st.subheader("Acronyms")
#                 acronyms = sections["Acronyms"].strip()
#                 if acronyms == "None identified in the conversation.":
#                     st.write("No acronyms were mentioned in the conversation.")
#                 else:
#                     st.markdown(acronyms)

#             with tab_objects[6]:
#                 st.subheader("Visualizations")
#                 if "visualizations" in st.session_state:
#                     if 'turn_count_plot' in st.session_state.visualizations and st.session_state.visualizations['turn_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['turn_count_plot']}",
#                             caption="Speaker Turn Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Turn count plot is not available.")

#                     if 'word_count_plot' in st.session_state.visualizations and st.session_state.visualizations['word_count_plot']:
#                         st.image(
#                             f"data:image/png;base64,{st.session_state.visualizations['word_count_plot']}",
#                             caption="Speaker Word Count Distribution",
#                             use_container_width=True,
#                         )
#                     else:
#                         st.warning("Word count plot is not available.")
#                 else:
#                     st.warning("No visualizations available.")

#             with tab_objects[7]:
#                 st.subheader("Transcription")
#                 if uploaded_file:
#                     try:
#                         filename = uploaded_file.name
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)
#                     except AttributeError:
#                         filename = st.session_state.selected_filename
#                         if filename.endswith(".mp4"):
#                             filename = filename.replace(".mp4", ".wav")
#                         st.markdown("### Audio Player and Interactive Transcription")
#                         audio_html = display_audio_player(
#                             st.session_state.transcription, 
#                             filename
#                         )
#                         components.html(audio_html, height=700)

# if __name__ == "__main__":
#     main()