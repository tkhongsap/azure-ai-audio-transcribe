import os
import requests
import json
from dotenv import load_dotenv
import glob
import re
from pathlib import Path
import time

# Load environment variables from .env file if it exists
try:
    load_dotenv()
    print("Loaded .env file")
except Exception as e:
    print(f"Note: Could not load .env file: {e}")
    print("Continuing with default values for testing...")

# Get API key and configuration from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "your_azure_api_key_here")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2025-03-01-preview")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4o-transcribe")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-transcribe")

if AZURE_OPENAI_API_KEY == "your_azure_api_key_here":
    print("Warning: Using placeholder API key. Set AZURE_OPENAI_API_KEY in .env for real transcriptions.")
    print("Will create dummy transcriptions for testing.")

# Azure OpenAI API endpoint
AZURE_TARGET_URI = f"https://ai-totrakoolk6076ai346198185670.openai.azure.com/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/audio/transcriptions?api-version={AZURE_API_VERSION}"

# Get the root directory of the project (the directory containing this script)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory containing audio files
SEGMENTS_DIR = os.path.join(ROOT_DIR, "output", "[Internal] OCR Logic_segments")
print(f"Looking for audio files in: {SEGMENTS_DIR}")

# Directory to save transcriptions
TRANSCRIPTS_DIR = os.path.join(ROOT_DIR, "output", "transcripts")
print(f"Transcripts will be saved to: {TRANSCRIPTS_DIR}")

# Create transcripts directory if it doesn't exist
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file using Azure OpenAI API
    """
    # Return dummy result if using placeholder API key
    if AZURE_OPENAI_API_KEY == "your_azure_api_key_here" or not os.path.exists(audio_file_path):
        return {"text": f"This is a dummy transcription for {os.path.basename(audio_file_path)}. Replace AZURE_OPENAI_API_KEY in .env with your actual key."}
        
    headers = {
        "Authorization": f"Bearer {AZURE_OPENAI_API_KEY}"
    }
    
    with open(audio_file_path, "rb") as audio_file:
        files = {
            "file": (os.path.basename(audio_file_path), audio_file, "audio/mp4")
        }
        data = {
            "model": AZURE_OPENAI_MODEL_NAME
        }
        
        response = requests.post(
            AZURE_TARGET_URI,
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def extract_part_number(filename):
    """Extract part number from filename, handling special characters"""
    match = re.search(r'part(\d+)', os.path.basename(filename))
    if match:
        return int(match.group(1))
    return 0  # Default value if no match found

def extract_base_name(filename):
    """Extract the base name of the file (without the part number and extension)"""
    base = os.path.basename(filename)
    # Remove part number and extension
    return re.sub(r'_part\d+\.[^.]+$', '', base)

def create_dummy_files():
    """Create dummy audio file paths for testing"""
    source_name = "[Internal] OCR Logic"
    dummy_files = []
    for i in range(1, 11):
        dummy_file = os.path.join(SEGMENTS_DIR, f"{source_name}_part{i:02d}.mp4")
        dummy_files.append(dummy_file)
    return dummy_files, source_name

def main():
    # Get all mp4 files in the segments directory
    audio_files = glob.glob(os.path.join(SEGMENTS_DIR, "*.mp4"))
    
    if not audio_files:
        print(f"No audio files found in {SEGMENTS_DIR}")
        # List directory contents to help diagnose the issue
        try:
            print("Contents of output directory:")
            for item in os.listdir(os.path.join(ROOT_DIR, "output")):
                print(f"  {item}")
        except Exception as e:
            print(f"Error listing directory: {e}")
        
        print("\nCreating dummy transcripts for testing purposes...")
        audio_files, source_name = create_dummy_files()
    else:
        # Get the common base name from the first file
        source_name = extract_base_name(audio_files[0])
    
    print(f"Found {len(audio_files)} audio files to transcribe")
    print(f"Source audio name: {source_name}")
    
    # Sort audio files numerically by their part number, handling special characters
    audio_files = sorted(audio_files, key=extract_part_number)
    
    # Display the sorted files
    print("Files will be processed in this order:")
    for i, file in enumerate(audio_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    all_transcriptions = []
    
    for audio_file in audio_files:
        file_name = os.path.basename(audio_file)
        base_name = os.path.splitext(file_name)[0]
        output_file = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.json")
        
        # Skip if already transcribed
        if os.path.exists(output_file):
            print(f"Reading existing transcription for {file_name}")
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    result = json.load(f)
                all_transcriptions.append({"segment": base_name, "text": result.get("text", "")})
            except json.JSONDecodeError:
                print(f"Error reading JSON from {output_file}, will retranscribe")
                os.remove(output_file)  # Remove invalid file
                # Continue to transcription below
            else:
                continue
        
        print(f"Transcribing {file_name}...")
        result = transcribe_audio(audio_file)
        
        if result:
            # Save individual transcription to file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Transcription saved to {output_file}")
            
            # Add to consolidated results
            all_transcriptions.append({"segment": base_name, "text": result.get("text", "")})
            
            # Add a small delay to avoid rate limiting (only if using real API)
            if AZURE_OPENAI_API_KEY != "your_azure_api_key_here":
                time.sleep(1)
        else:
            print(f"Failed to transcribe {file_name}")
    
    # Save consolidated transcription
    if all_transcriptions:
        # Create a combined text version
        consolidated_text = "\n\n".join([f"# {item['segment']}\n{item['text']}" for item in all_transcriptions])
        
        # Save as text file with the source name
        consolidated_text_file = os.path.join(TRANSCRIPTS_DIR, f"{source_name}_transcript.txt")
        with open(consolidated_text_file, "w", encoding="utf-8") as f:
            f.write(consolidated_text)
        print(f"Consolidated transcript saved to {consolidated_text_file}")
        
        # Save as JSON file with the source name
        consolidated_json_file = os.path.join(TRANSCRIPTS_DIR, f"{source_name}_transcript.json")
        with open(consolidated_json_file, "w", encoding="utf-8") as f:
            json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)
        print(f"Consolidated JSON transcript saved to {consolidated_json_file}")

if __name__ == "__main__":
    main()
