

import base64
from collections import Counter
import io
import re
import PyPDF2
import seaborn as sns
from matplotlib import pyplot as plt
from src.services.azure_openai import client
import logging

logger = logging.getLogger(__name__)

def extract_speaker_turns_and_word_count(text):
    """Extracts the number of times each speaker has spoken and their respective word count.
    """
    
    # Initialize counters for speaker turns and word count
    speaker_turns = Counter()
    word_count = Counter()
    
    # Find all speaker labels (e.g., "Guest 1:", "Guest 2:") in the text
    speakers = re.findall(r"(Guest \d+):", text)
    
    # Count the number of times each speaker appears
    for speaker in speakers:
        speaker_turns[speaker] += 1
    
    # Count the number of words spoken by each speaker
    for speaker in speaker_turns:
        words = re.findall(rf"{speaker}: (.*?)\n", text, re.DOTALL)  # Extract the speech lines
        word_count[speaker] = sum(len(word.split()) for word in words)  # Count words for each line
    
    return speaker_turns, word_count


def extract_topic_segmentation(text):
    """Extracts topic segmentation from the transcribed text.
    
    This function identifies numbered topics within the text using a regex pattern.
    """
    
    # Find all numbered topics in the format "1. Topic title" followed by a timestamp
    topics = re.findall(r"(\d+\.\s.*?)(?=\s\d+\.|$)", text)
    
    # Convert extracted topics into a dictionary mapping topic names to timestamps
    return {topic: int(time) for topic, time in topics}


def create_visualization_plots(speaker_turn_count, total_word_count):
    """Creates visualizations for speaker turn counts and word counts, and returns them as base64-encoded images.
    
    Generates:
    - A pie chart showing the proportion of speaker turns.
    - A bar graph showing the total word count spoken by each speaker.
    """
    
    # Create Speaker Turn Count Pie Chart
    plt.figure(figsize=(10, 7))
    plt.pie(
        speaker_turn_count.values(),  # Proportions based on turn counts
        labels=speaker_turn_count.keys(),  # Speaker labels
        autopct="%1.1f%%",  # Show percentage values on the chart
        startangle=140,  # Rotate for better visualization
    )
    plt.title("Speaker Turn Count")  # Add chart title

    # Save the pie chart to an in-memory buffer
    turn_count_buffer = io.BytesIO()
    plt.savefig(turn_count_buffer, format="png")
    turn_count_buffer.seek(0)
    
    # Convert the image buffer to a base64-encoded string
    turn_count_image = base64.b64encode(turn_count_buffer.getvalue()).decode()
    plt.close()

    # Create Word Count Bar Graph
    plt.figure(figsize=(10, 7))
    sns.barplot(x=list(total_word_count.keys()), y=list(total_word_count.values()))
    plt.title("Total Word Count")  # Add chart title
    plt.xlabel("Speakers")  # Label x-axis
    plt.ylabel("Word Count")  # Label y-axis
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability

    # Save the bar graph to an in-memory buffer
    word_count_buffer = io.BytesIO()
    plt.savefig(word_count_buffer, format="png")
    word_count_buffer.seek(0)
    
    # Convert the image buffer to a base64-encoded string
    word_count_image = base64.b64encode(word_count_buffer.getvalue()).decode()
    plt.close()

    return turn_count_image, word_count_image  # Return the base64-encoded images


def analyze_transcript(pdf_path):
    """Extracts text from a PDF transcript and processes it using an AI model to generate structured information.
    """

    # Log entry point for debugging
    logger.info("I am in analyze_transcript function")

    # Initialize an empty string to hold the extracted PDF content
    file_content = ""

    # Open the PDF file in binary read mode
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
        
    # Log before making the API call
    logger.info("I am just before API call...")

    # Make an API call to process the transcript
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
    
    # Return AI-generated report and raw transcript text
    return res.choices[0].message.content, file_content


def generate_answer(question, transcription_text):
    """Generates a structured AI response based on a given question and the provided transcript.
    """

    # Construct AI prompt with the given context
    prompt = f"""
    You are an intelligent assistant. Answer the following question concisely.

    Context (if available):
    {transcription_text}

    Question:
    {question}

    Provide a clear and structured answer in a professional tone.
    """

    try:
        # Make an API call to generate an answer
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides clear and concise answers.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,  # Controls randomness in responses
            max_tokens=1000,  # Limits response length
            top_p=0.6,  # Nucleus sampling parameter
            frequency_penalty=0.7,  # Reduces repetitive outputs
        )

        # Log API response for debugging
        print(response)

        # Return AI-generated answer
        return response.choices[0].message.content

    except Exception as e:
        # Handle API errors gracefully
        return f"Error generating response: {str(e)}"
