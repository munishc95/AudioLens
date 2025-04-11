import base64
import io
from flask import Blueprint, Response, request, jsonify, send_file
import yt_dlp
from src.utils.url_utils import get_video_id
from src.services.transcriber import Transcriber
from src.config.settings import subscription_key, region
from src.utils.transcript_utils import analyze_transcript, extract_speaker_turns_and_word_count, extract_topic_segmentation, create_visualization_plots
from src.utils.ask_utils import generate_answer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
import logging


# Initialize logger
logger = logging.getLogger(__name__)

app = Blueprint("audio", __name__)

# data storing directories
INPUT_DIR = r"data/input/"
OUTPUT_DIR = r"data/output/"
ROOT_DIR = os.getcwd()
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/download_youtube_audio", methods=["POST"])
def download_youtube_audio():
    """
    This function download the audio through url and save the audio file in data/input directory.
    """
    
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Get video ID and title
        video_id, original_title = get_video_id(url)
        if not video_id:
            return jsonify({"error": "Failed to extract video details"}), 400

        root_file_path = os.path.join(ROOT_DIR, f"{video_id}.wav")
        sanitized_file_path = os.path.join(INPUT_DIR, f"{video_id}.wav")

        # Check if the file already exists
        if os.path.exists(sanitized_file_path):
            logger.info(f"File already exists: {sanitized_file_path}, returning existing file.")
            return jsonify({"audio_file_path": sanitized_file_path}), 200

        # yt-dlp options for downloading
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
            "outtmpl": os.path.join(INPUT_DIR, f"{video_id}.%(ext)s"),
        }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Verify download
        downloaded_file_path = os.path.join(INPUT_DIR, f"{video_id}.wav")
        if not os.path.exists(downloaded_file_path):
            logger.error(f"Download failed: {downloaded_file_path}")
            return jsonify({"error": "File download failed"}), 500


        logger.info(f"Audio file saved as: {downloaded_file_path}")
        return jsonify({"audio_file_path": downloaded_file_path}), 200

    except Exception as e:
        logger.error(f"Error during YouTube audio download: {str(e)}")
        return jsonify({"error": str(e)}), 500


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

    
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """This function generate pdf and return file in response."""
    
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


@app.route('/stream-audio/<filename>', methods=["GET"])
def stream_audio(filename):
    """This function streams the audio file in chunks to the client."""
    
    # Log the streaming request for the specified file
    logger.info(f'Streaming request for {filename}...')

    # Construct the full path to the audio file using the INPUT_DIR constant
    file_path = os.path.join(INPUT_DIR, filename)

    # Check if the file exists at the specified path
    if not os.path.exists(file_path):
        # Log an error if the file is not found
        logger.error(f"File not found: {file_path}")
        # Return an error response with a 404 status code if file is not found
        return jsonify({"error": "File not found"}), 404

    # Define a generator function to stream the file in chunks
    def generate():
        # Open the audio file in binary read mode
        with open(file_path, 'rb') as audio_file:
            # Read and yield 1MB chunks at a time until the end of the file
            while chunk := audio_file.read(1024 * 1024):  # 1MB chunk size
                yield chunk

    # Return a Response object that streams the audio in chunks
    # Set the mimetype to 'audio/wav' for WAV audio format
    return Response(generate(), mimetype='audio/wav')


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """This function handles the transcription of audio files."""
    
    try:
        logger.info("I am in transcribe")
        # Handle audio file upload
        audio_file = request.files["file"]
        
        if not audio_file:
            return jsonify({"error": "No audio file provided"}), 400

        # Save the uploaded audio file
        audio_filename = os.path.join(ROOT_DIR, INPUT_DIR, audio_file.filename)
        print(f"Audio file path: {audio_filename}")
        audio_file.save(audio_filename)  # Save the file to the specified path
        
        logger.info(f"Attempting to transcribe file: {audio_filename}")
        logger.info(f"File exists: {os.path.exists(audio_filename)}")
        

        # Check if the PDF already exists
        pdf_filename = (
            f"{OUTPUT_DIR}{os.path.splitext(audio_file.filename)[0]}.pdf"
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
            pdf_filename = transcriber.save_to_pdf(audio_name=audio_file.filename, output_dir=OUTPUT_DIR)
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
        print(f"Error in transcribe: {str(e)}")
        return jsonify({"error": str(e)}), 500
