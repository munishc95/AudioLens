import yt_dlp
import logging

logger = logging.getLogger(__name__)

def get_video_id(url):
    """Extracts the video ID and title from a YouTube URL using yt-dlp."""
    
    try:
        # Use yt-dlp with quiet mode enabled to suppress unnecessary logs
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            # Extract metadata from the given URL without downloading the video
            info_dict = ydl.extract_info(url, download=False)
            
            # Return the extracted video ID and title
            return info_dict["id"], info_dict["title"]
    
    except Exception as e:
        # Log an error message if extraction fails
        logger.error(f"Error extracting video ID: {str(e)}")
        
        # Return None for both video ID and title in case of an error
        return None, None
