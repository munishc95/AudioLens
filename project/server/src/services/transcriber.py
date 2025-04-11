import os
import time
import azure.cognitiveservices.speech as speechsdk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from moviepy import VideoFileClip
from pydub import AudioSegment

"""This class transcribes audio files using Azure Speech Services."""
class Transcriber:
    def __init__(self, subscription_key, region, audio_filename):
        """This function is constructor for class Transcriber and initialize the class variables."""

        # Extract audio from MP4 if needed
        if audio_filename.endswith(".mp4"):
            video = VideoFileClip(audio_filename)
            audio_filename = audio_filename.replace(".mp4", ".wav")
            video.audio.write_audiofile(audio_filename, codec="pcm_s16le")

        # Convert MP3 to WAV if needed
        if audio_filename.endswith(".mp3"):
            print("Error before segnemt")
            audio = AudioSegment.from_mp3(audio_filename)
            audio_filename = audio_filename.replace(".mp3", ".wav")
            print("error before")
            audio.export(out_f=audio_filename, format="wav")

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
        """This function sets up the callbacks for the conversation transcriber."""
        
        self.conversation_transcriber.transcribed.connect(self.transcribed_cb)
        self.conversation_transcriber.transcribing.connect(self.transcribing_cb)
        self.conversation_transcriber.session_started.connect(self.session_started_cb)
        self.conversation_transcriber.session_stopped.connect(self.session_stopped_cb)
        self.conversation_transcriber.canceled.connect(self.canceled_cb)
        self.conversation_transcriber.session_stopped.connect(self.stop_cb)
        self.conversation_transcriber.canceled.connect(self.stop_cb)

    def get_guest_label(self, speaker_id):
        """This function returns the guest label for the given speaker ID."""
        
        # Check if speaker_id is provided; if not, assign it as "None"
        if not speaker_id:
            speaker_id = "None"

        # If the speaker_id is not already mapped, assign a new label
        if speaker_id not in self.speaker_mapping:
            # If there are fewer than 2 speakers mapped, assign from predefined guest labels
            if len(self.speaker_mapping) < 2:
                self.speaker_mapping[speaker_id] = self.guest_labels[len(self.speaker_mapping)]
            else:
                # If speaker_id is "None", assign label as "Unknown"
                # Otherwise, assign a new guest label dynamically
                self.speaker_mapping[speaker_id] = (
                    "Unknown" if speaker_id == "None" else f"Guest {len(self.speaker_mapping) + 1}"
                )
    
        # Return the assigned guest label for the speaker
        return self.speaker_mapping[speaker_id]

    def format_time(self, offset):
        """This function format the time properly."""
        
        seconds = offset / 10_000_000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        """Callback function triggered when speech is transcribed.
        
        Processes the recognized speech, assigns a speaker label, formats the timestamp, 
        and stores the transcription result.
        """

        # Check if the speech recognition result is valid
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Get the speaker label based on the speaker ID
            speaker_label = self.get_guest_label(evt.result.speaker_id)
            
            # Format the timestamp from the speech event
            timestamp = self.format_time(evt.result.offset)
            
            # Construct the formatted transcription text
            result_text = f"[{timestamp}] {speaker_label}: {evt.result.text}"
            
            # Print the transcribed text
            print(result_text)
            
            # Store the transcription result
            self.transcription_results.append(result_text)
        
        # Handle case where no speech is recognized
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            pass  # No action needed if no speech is recognized


    def transcribing_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):  
        """Callback function triggered during ongoing speech transcription.
        
        Processes interim recognized speech, assigns a speaker label, formats the timestamp, 
        and appends the result to the transcription list.
        """

        # Check if the speech recognition event contains recognized speech
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Retrieve the speaker label based on the speaker ID
            speaker_label = self.get_guest_label(evt.result.speaker_id)
            
            # Format the timestamp from the speech event offset
            timestamp = self.format_time(evt.result.offset)
            
            # Construct the formatted transcription text with timestamp and speaker label
            result_text = f"[{timestamp}] {speaker_label}: {evt.result.text}"
            
            # Print the transcribed text to the console
            print(result_text)
            
            # Store the transcribed result in the transcription results list
            self.transcription_results.append(result_text)


    def session_started_cb(self, evt):
        """Session started callback function."""
        """Handles session start events during speech recognition."""
        pass

    def session_stopped_cb(self, evt):
        """Session stopped callback function."""
        """Handles session stop events during speech recognition."""
        pass

    def canceled_cb(self, evt):
        """Canceled callback function."""
        """Handles cancellation events during speech recognition."""
        pass

    def stop_cb(self, evt):
        """Stop callback function."""
        """Handles stop events during speech recognition."""
        """Sets the transcribing_stop flag to True when the session is stopped."""
        self.transcribing_stop = True

    def recognize_from_file(self):
        """Starts the transcription process asynchronously."""
        """This function starts the transcription process asynchronously."""
        self.conversation_transcriber.start_transcribing_async()
        while not self.transcribing_stop:
            time.sleep(0.5)
        self.conversation_transcriber.stop_transcribing_async()

    def save_to_pdf(self, audio_name, output_dir):
        """Saves the transcribed text to a PDF file inside the specified output directory."""

        # Generate the PDF filename by replacing the audio file extension with ".pdf"
        pdf_filename = audio_name
        if pdf_filename.endswith(".mp3"):
            pdf_filename = pdf_filename.replace(".mp3", ".pdf")
        elif pdf_filename.endswith(".mp4"):
            pdf_filename = pdf_filename.replace(".mp4", ".pdf")
        elif pdf_filename.endswith(".wav"):
            pdf_filename = pdf_filename.replace(".wav", ".pdf")

        # Construct the full file path for the PDF
        pdf_path = os.path.join(output_dir, pdf_filename)

        # Create a PDF document template with letter-sized pages
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []  # List to hold elements (text, spacing) for the PDF content
        styles = getSampleStyleSheet()  # Load predefined styles

        # Add the title "Transcription" to the PDF with a predefined title style
        title_style = styles["Title"]
        elements.append(Paragraph("Transcription", title_style))
        elements.append(Spacer(1, 12))  # Add space after the title

        # Define colors for different guest speakers in the transcription
        guest_colors = {
            "Guest 1": colors.navy,
            "Guest 2": colors.teal,
            "Guest 3": colors.grey,
            "Guest 4": colors.green,
        }

        # Set the default paragraph style for the transcription text
        para_style = styles["BodyText"]
        para_style.alignment = 4  # Justify text alignment

        # Iterate through each transcribed line and add it to the PDF
        for line in self.transcription_results:
            guest_label = line.split(":")[0]  # Extract speaker label (e.g., "Guest 1")
            
            # Assign a color to the text based on the speaker label
            para_style.textColor = guest_colors.get(guest_label, colors.black)
            
            # Add the transcribed line to the document with the assigned style
            elements.append(Paragraph(line, para_style))
            elements.append(Spacer(1, 12))  # Add space after each line for readability

        # Build and save the PDF with the added elements
        doc.build(elements)

        # Print confirmation message and return the generated PDF path
        print(f"Transcription saved to {pdf_path}")
        return pdf_path
