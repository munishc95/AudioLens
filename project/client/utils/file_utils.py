import os

def get_existing_files(folder_path):
    """Get list of existing wav files in input folder"""
    wav_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".wav"):
            wav_files.append(file)
    return wav_files