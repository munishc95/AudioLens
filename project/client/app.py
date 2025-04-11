
import streamlit as st
import time
import requests
import io
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

from utils.file_utils import get_existing_files
from utils.frontent_utils import display_audio_player, display_chat_with_audio
from utils.text_utils import extract_companies, extract_guest_names, get_analysis_sections

load_dotenv()

backendendpoint = os.getenv("backendendpoint")
print("bc ",backendendpoint)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Path of client/
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "server", "data"))

print("BASE",BASE_DIR)
print("data",DATA_DIR)

INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    """This function is the main entry point of the Streamlit app."""
    
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
        existing_files = get_existing_files(INPUT_DIR)
        if existing_files:
            selected_filename = st.selectbox(
                "Select an existing recording", existing_files
            )
            if selected_filename:
                selected_file = f"{INPUT_DIR}/{selected_filename}"
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
                    selected_file = os.path.join(INPUT_DIR, selected_filename)

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