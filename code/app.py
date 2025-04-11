from flask import Flask, request, jsonify, send_file, Response
import os
import time
import azure.cognitiveservices.speech as speechsdk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from collections import Counter
import PyPDF2
from moviepy import VideoFileClip
import matplotlib.pyplot as plt
import requests
import seaborn as sns
from openai import AzureOpenAI
import re
from fpdf import FPDF
from dotenv import load_dotenv
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import matplotlib
from pydub import AudioSegment
from pydub.utils import mediainfo
import yt_dlp
# AudioSegment.converter = os.getcwd()+ "\\ffmpeg.exe"                    
# AudioSegment.ffprobe   = os.getcwd()+ "\\ffprobe.exe"
import logging
import wave

logging.basicConfig(
    level=logging.INFO,  # Set the log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler()  # Output logs to console
    ]
)
matplotlib.use("agg")

current_file_path = os.path.abspath(__file__)
current_folder_path = os.path.dirname(current_file_path)
current_folder_path = f"{current_folder_path}/input/"
# print(f"Current folder path: {current_folder_path}")
app = Flask(__name__)
logger = logging.getLogger(__name__)

load_dotenv()

# Azure OpenAI configuration
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
subscription_key = os.getenv("subscription_key")
region = os.getenv("region")
# infilelocation = os.getenv("infilelocation")
# outfilelocation = os.getenv("outfilelocation")

backendendpoint = os.getenv("backendendpoint")
client = AzureOpenAI(
    api_version=OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)

def sanitize_filename(filename):
    """Removes special characters from filenames to prevent errors."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in filename)


def get_audio_duration(file_path):
    """Returns the duration of an audio file in seconds."""
    try:
        with wave.open(file_path, "r") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            return frames / float(rate)
    except Exception as e:
        logger.error(f"Error getting duration for {file_path}: {str(e)}")
        return None



class Transcriber:
    def __init__(self, subscription_key, region, audio_filename):

        # Extract audio from MP4 if needed
        if audio_filename.endswith('.mp4'):
            video = VideoFileClip(audio_filename)
            audio_filename = audio_filename.replace('.mp4', '.wav')
            video.audio.write_audiofile(audio_filename, codec='pcm_s16le')
 
        # Convert MP3 to WAV if needed
        if audio_filename.endswith('.mp3'):
            print('Error before segnemt')
            audio = AudioSegment.from_mp3(audio_filename)
            audio_filename = audio_filename.replace('.mp3', '.wav')
            print('error before')
            audio.export(out_f = audio_filename, format='wav')
            
            print("succesfully converted mp3 to wav")
 
        self.speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key, region=region
        )
        self.speech_config.speech_recognition_language = "en-US"
        self.speech_config.set_property(
            property_id=speechsdk.PropertyId.SpeechServiceResponse_DiarizeIntermediateResults,
            value="true",
        )
        # Enable speaker diarization (identify different speakers)
        self.speech_config.set_property(
            property_id=speechsdk.PropertyId.SpeechServiceResponse_JsonResult,
            value="true",
        )
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)
        self.conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
            speech_config=self.speech_config, audio_config=self.audio_config
        )
        self.speaker_mapping = {}
        self.guest_labels = ["Guest 1", "Guest 2"]
        self.transcribing_stop = False
        self.transcription_results = []
        self.setup_callbacks()

    def setup_callbacks(self):
        self.conversation_transcriber.transcribed.connect(self.transcribed_cb)
        self.conversation_transcriber.transcribing.connect(self.transcribing_cb)
        self.conversation_transcriber.session_started.connect(self.session_started_cb)
        self.conversation_transcriber.session_stopped.connect(self.session_stopped_cb)
        self.conversation_transcriber.canceled.connect(self.canceled_cb)
        self.conversation_transcriber.session_stopped.connect(self.stop_cb)
        self.conversation_transcriber.canceled.connect(self.stop_cb)

    def get_guest_label(self, speaker_id):
        if not speaker_id:
            speaker_id = "None"
        if speaker_id not in self.speaker_mapping:
            if len(self.speaker_mapping) < 2:
                self.speaker_mapping[speaker_id] = self.guest_labels[
                    len(self.speaker_mapping)
                ]
            else:
                self.speaker_mapping[speaker_id] = (
                    "Unknown"
                    if speaker_id == "None"
                    else f"Guest {len(self.speaker_mapping) + 1}"
                )
        return self.speaker_mapping[speaker_id]

    def format_time(self, offset):
        seconds = offset / 10_000_000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            speaker_label = self.get_guest_label(evt.result.speaker_id)
            timestamp = self.format_time(evt.result.offset)
            result_text = f"[{timestamp}] {speaker_label}: {evt.result.text}"
            print(result_text)
            self.transcription_results.append(result_text)
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            pass

    def transcribing_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            speaker_label = self.get_guest_label(evt.result.speaker_id)
            timestamp = self.format_time(evt.result.offset)
            result_text = f"[{timestamp}] {speaker_label}: {evt.result.text}"
            print(result_text)
            self.transcription_results.append(result_text)

    def session_started_cb(self, evt):
        pass

    def session_stopped_cb(self, evt):
        pass

    def canceled_cb(self, evt):
        pass

    def stop_cb(self, evt):
        self.transcribing_stop = True

    def recognize_from_file(self):
        self.conversation_transcriber.start_transcribing_async()
        while not self.transcribing_stop:
            time.sleep(0.5)
        self.conversation_transcriber.stop_transcribing_async()

    def save_to_pdf(self, audio_name):
        # pdf_filename = audio_name.replace(".wav", ".pdf")
        if audio_name.endswith('.mp3'):
            pdf_filename = audio_name.replace('.mp3', '.pdf')
 
        if audio_name.endswith('.mp4'):
            pdf_filename = audio_name.replace('.mp4', '.pdf')
 
        if audio_name.endswith('.wav'):
            pdf_filename = audio_name.replace(".wav", ".pdf")
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title = Paragraph("Transcription", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        guest_colors = {
            "Guest 1": colors.navy,
            "Guest 2": colors.teal,
            "Guest 3": colors.grey,
            "Guest 4": colors.green,
        }

        para_style = styles["BodyText"]
        para_style.alignment = 4

        for line in self.transcription_results:
            guest_label = line.split(":")[0]
            para_style.textColor = guest_colors.get(guest_label, colors.black)
            paragraph = Paragraph(line, para_style)
            elements.append(paragraph)
            elements.append(Spacer(1, 12))

        doc.build(elements)
        print(f"Transcription saved to {pdf_filename}")
        return pdf_filename



# Extract dynamic data
def extract_speaker_turns_and_word_count(text):
    speaker_turns = Counter()
    word_count = Counter()
    speakers = re.findall(r"(Guest \d+):", text)
    for speaker in speakers:
        speaker_turns[speaker] += 1
    for speaker in speaker_turns:
        words = re.findall(rf"{speaker}: (.*?)\n", text, re.DOTALL)
        word_count[speaker] = sum(len(word.split()) for word in words)
    return speaker_turns, word_count


def extract_topic_segmentation(text):
    topics = re.findall(r"(\d+\.\s.*?)(?=\s\d+\.|$)", text)
    return {topic: int(time) for topic, time in topics}


def create_visualization_plots(speaker_turn_count, total_word_count):
    """Create and return base64 encoded plot images"""
    # Speaker Turn Count Pie Chart
    plt.figure(figsize=(10, 7))
    plt.pie(
        speaker_turn_count.values(),
        labels=speaker_turn_count.keys(),
        autopct="%1.1f%%",
        startangle=140,
    )
    plt.title("Speaker Turn Count")

    # Save to bytes buffer
    turn_count_buffer = io.BytesIO()
    plt.savefig(turn_count_buffer, format="png")
    turn_count_buffer.seek(0)
    turn_count_image = base64.b64encode(turn_count_buffer.getvalue()).decode()
    plt.close()

    # Word Count Bar Graph
    plt.figure(figsize=(10, 7))
    sns.barplot(x=list(total_word_count.keys()), y=list(total_word_count.values()))
    plt.title("Total Word Count")
    plt.xlabel("Speakers")
    plt.ylabel("Word Count")
    plt.xticks(rotation=45)

    # Save to bytes buffer
    word_count_buffer = io.BytesIO()
    plt.savefig(word_count_buffer, format="png")
    word_count_buffer.seek(0)
    word_count_image = base64.b64encode(word_count_buffer.getvalue()).decode()
    plt.close()

    return turn_count_image, word_count_image


def analyze_transcript(pdf_path):
    # Read PDF content
    logger.info("I am in analyze_transcript function")
    file_content = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            file_content += page.extract_text()

    prompt = f"""
        You are a helpful assistant. Here is a text Please read the prompt twice so that you understand
        {file_content}
        Note :-Please Do not bold or highlight any text,let the output be normal & properly format the spacing and alignments:
        
        Details of speaker
        
        Please read the transcript twice and identify the Names of speakers, their designations, and company names. You can figure out the names of speakers where available, especially in conversations where greetings like "hi" or "hello" are exchanged. Provide the details in the following format:
        
        Guest 1:
        Designation & Company:
        Guest 2:
        Designation & Company:
        SUMMARY
        
        Provide a combined detailed summary of the utterances from the PDF. The summary should be readable, with each line containing a few words before moving to the next line. Ensure the summary fits one page and is written in a single paragraph. Title the section as "SUMMARY" with a font size of 16.
        Question and Answer
        
        You have a transcription document that includes accurate timestamps for each speaker.
        Transcription is conversation between persons and questions are asked in it.
        Your task is to extract all the questions asked  in the transcription along with its timestamp.
        It is crucial to maintain the original timestamp from the transcription and present it in a consistent format (e.g., HH:MM:SS).
        Instructions:
        Carefully identify the portions of the text where questions are asked.
        Extract the exact timestamp associated with each question as it appears in the transcription.
        Ensure that the extracted timestamps are presented in the format HH:MM:SS.
        Note: you can make use of pattern = r'\[(\d{2}:\d{2}:\d{2})\] Guest \d+: (.*?\?)' to identify the questions. and you can extract answers from transcription.
        [extracted timestamp] Question 1:
        Answer:
        [extracted timestamp] Question 2:
        Answer:
        
        LIST OF COMPANIES
        
        List all the companies discussed in the conversation. Title the section as "LIST OF COMPANIES" with a font size of 16. Ensure to list only the companies mentioned in the PDF also mention one liner about the company and URL of that company.
        Sentiment Over Time
        
        Provide the overall sentiment along with it please provide the statements that supports overall sentiments.
        Also, make separate paragraphs for positive, negative an neutral statements.
        
        Acronyms and Full Forms
        
        List all the acronyms and their full forms relevant to the topic of conversation.
        
        List out all the action items from the transcription with a font size of 16.
        
        *Note Check everything again and provide all the information asked in detail
        please dont write any notes at the end of report generated and remove any "*" or "#" used for highlighting title *
        """
    logger.info("I am just before API call...")
    # Make the API call
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear and concise summaries.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7,
    )

    return res.choices[0].message.content, file_content


def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict["id"], info_dict["title"]
    except Exception as e:
        logger.error(f"Error extracting video ID: {str(e)}")
        return None, None

def generate_answer(question, transcription_text):
    """Generates an AI response using prompt engineering with transcription context."""
    prompt = f"""
    You are an intelligent assistant. Answer the following question concisely.
    
    Context (if available):
    {transcription_text}
    
    Question:
    {question}
    
    Provide a clear and structured answer in a professional tone.
    """
    
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear and concise answers.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7,
        )
        
        print(response)
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Get data from request
    data = request.json
    sections = data.get('sections', {})
    transcription = data.get('transcription', '')
    visualizations = data.get('visualizations', [])

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add Names & Entities section first
    if "Names & Entities" in sections:
        story.append(Paragraph("Names & Entities", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add Guest Names
        story.append(Paragraph("Guest Names", styles['Heading2']))
        for name in sections["Names & Entities"].get("Guest Names", "").split('\n'):
            story.append(Paragraph(name, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Add Companies
        story.append(Paragraph("Companies", styles['Heading2']))
        for company in sections["Names & Entities"].get("Companies", "").split('\n'):
            story.append(Paragraph(company, styles['Normal']))
        
        story.append(Spacer(1, 12))
        
        # Remove Names & Entities from sections to avoid duplicate processing
        del sections["Names & Entities"]

    # Process remaining sections (as before)
    for section_name, section_content in sections.items():
        # Add section title
        story.append(Paragraph(section_name, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Add section content
        if isinstance(section_content, dict):
            # Handle nested sections (like Names & Entities)
            for subsection, content in section_content.items():
                story.append(Paragraph(subsection, styles['Heading2']))
                paragraphs = content.split('\n')
                for para in paragraphs:
                    story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 12))
        else:
            # Handle regular sections
            paragraphs = section_content.split('\n')
            for para in paragraphs:
                story.append(Paragraph(para, styles['Normal']))
        
        story.append(Spacer(1, 12))
    story.append(Paragraph("Visualizations", styles['Heading1']))
    for viz_base64 in visualizations:
        # Decode base64 image
        image_bytes = base64.b64decode(viz_base64)
        image_stream = io.BytesIO(image_bytes)
        
        # Add image to PDF
        img = Image(image_stream)
        img.drawHeight = 3*inch
        img.drawWidth = 5*inch
        story.append(img)
        story.append(Spacer(1, 12))

    # Add full transcription at the end
    story.append(Paragraph("Full Transcription", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Split transcription into paragraphs
    transcription_paragraphs = transcription.split('\n')
    for para in transcription_paragraphs:
        story.append(Paragraph(para, styles['Normal']))

    # Build PDF
    doc.build(story)

    # Move buffer pointer to beginning
    buffer.seek(0)

    # Send file
    return send_file(
        buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name='meeting_summary.pdf'
    )


@app.route("/ask", methods=["POST"])
def ask():
    """API route to handle question answering with transcription data."""
    data = request.get_json()
    question = data.get("question")
    transcription_text = data.get("transcription_text", "")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    answer = generate_answer(question, transcription_text)
    
    return jsonify({"question": question, "answer": answer})


@app.route('/stream-audio/<filename>', methods=["GET"])
def stream_audio(filename):
    logger.info(f'Streaming request for {filename}...')

    file_path = os.path.join(current_folder_path, filename)  # Don't append .wav

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return jsonify({"error": "File not found"}), 404

    def generate():
        with open(file_path, 'rb') as audio_file:
            while chunk := audio_file.read(1024 * 1024):  # Read 1MB at a time
                yield chunk

    return Response(generate(), mimetype='audio/wav')



@app.route("/download_youtube_audio", methods=["POST"])
def download_youtube_audio():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Get video ID and title
        video_id, original_title = get_video_id(url)
        if not video_id:
            return jsonify({"error": "Failed to extract video details"}), 400

        sanitized_file_path = os.path.join(current_folder_path, f"{video_id}.wav")

        # Check if the file already exists
        if os.path.exists(sanitized_file_path):
            logger.info(f"File already exists: {sanitized_file_path}, returning existing file.")
            return jsonify({"audio_file_path": sanitized_file_path}), 200

        # yt-dlp options for downloading
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
            "outtmpl": os.path.join(current_folder_path, f"{video_id}.%(ext)s"),
        }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Verify download
        downloaded_file_path = os.path.join(current_folder_path, f"{video_id}.wav")
        if not os.path.exists(downloaded_file_path):
            logger.error(f"Download failed: {downloaded_file_path}")
            return jsonify({"error": "File download failed"}), 500

        logger.info(f"Audio file saved as: {downloaded_file_path}")
        return jsonify({"audio_file_path": downloaded_file_path}), 200

    except Exception as e:
        logger.error(f"Error during YouTube audio download: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        logger.info("I am in transcribe")
        # Handle audio file upload
        # print('reached here')
        # print(request)
        audio_file = request.files["file"]
        # print('reached here')
        if not audio_file:
            return jsonify({"error": "No audio file provided"}), 400

        # Save the uploaded audio file
        audio_filename = f"{current_folder_path}{audio_file.filename}"
        print(audio_filename)
        audio_file.save(audio_filename)

        # Check if the PDF already exists
        pdf_filename = (
            f"{current_folder_path}{os.path.splitext(audio_file.filename)[0]}.pdf"
        )

        if os.path.exists(pdf_filename):
            logger.info("I am in analyze_transcript")
            # Extract transcription and summary from existing PDF
            summary, text_to_send = analyze_transcript(pdf_filename)
            logger.info("I am in analyze_transcript-1")
            # Generate visualizations from existing content
            speaker_turn_count, total_word_count = extract_speaker_turns_and_word_count(
                text_to_send
            )
            logger.info("I am in analyze_transcript-2")
            turn_count_plot, word_count_plot = create_visualization_plots(
                speaker_turn_count, total_word_count
            )
        else:
            logger.info("I am in Transcriber-step-0")
            # Perform new transcription
            print("reacahed till transcription")
            print(audio_filename)
            transcriber = Transcriber(subscription_key, region, audio_filename)
            logger.info("I am in Transcriber-"
            "step-1")
            transcriber.recognize_from_file()
            logger.info("I am in Transcriber-step-2")
            print('rreaches after transcription')
            # Save transcription to PDF
            pdf_filename = transcriber.save_to_pdf(audio_name=audio_filename)
            logger.info("I am in Transcriber-step-3")
            # Build transcription text
            text_to_send = "\n".join(transcriber.transcription_results)
            logger.info("I am in Transcriber-step-4")
            # Generate summary using OpenAI
            summary, _ = analyze_transcript(pdf_filename)
            logger.info("I am in Transcriber-step-5")
            # Generate visualizations from new transcription
            speaker_turn_count, total_word_count = extract_speaker_turns_and_word_count(
                text_to_send
            )
            turn_count_plot, word_count_plot = create_visualization_plots(
                speaker_turn_count, total_word_count
            )

        return jsonify(
            {
                "transcription": text_to_send,
                "summary": summary[0] if isinstance(summary, tuple) else summary,
                "pdf_path": pdf_filename,
                "visualizations": {
                    "turn_count_plot": turn_count_plot,
                    "word_count_plot": word_count_plot,
                },
            }
        )

    except Exception as e:
        print(f"Error in transcribe: {str(e)}")  # Debug logging
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
