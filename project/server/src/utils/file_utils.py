import re
import wave
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Removes invalid characters from filenames for Windows.
    
    Windows does not allow certain special characters in filenames. 
    This function removes any invalid characters to ensure compatibility.
    """
    
    # Use regular expressions to remove invalid characters: <>:"/\|?*
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Log the sanitized filename for debugging or tracking purposes
    logger.info(f"Sanitized filename: {sanitized}")
    
    return sanitized


def get_audio_duration(file_path):
    """Returns the duration of an audio file in seconds.
    
    This function reads the audio file's metadata to calculate the total duration
    in seconds by dividing the number of frames by the frame rate.
    """
    
    try:
        # Open the audio file in read mode
        with wave.open(file_path, "r") as audio:
            frames = audio.getnframes()  
            rate = audio.getframerate()  
            
            # Compute the duration in seconds
            duration = frames / float(rate)
            
            # Log the computed audio duration
            logger.info(f"Audio duration for {file_path}: {duration:.2f} seconds")
            
            return duration

    except Exception as e:
        # Log any errors that occur while processing the file
        logger.error(f"Error getting duration for {file_path}: {str(e)}", exc_info=True)
        
        return None
