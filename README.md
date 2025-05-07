# Audio Transcription with Azure OpenAI

This script uses Azure OpenAI's GPT-4o Transcribe model to transcribe MP4 audio files.

## Setup

1. Install the required dependencies:
   ```
   pip install requests python-dotenv
   ```

2. Create a `.env` file in the root directory with your Azure API key:
   ```
   AZURE_API_KEY=your_azure_api_key_here
   ```

3. Place your MP4 audio files in the `output/[Internal] OCR Logic_segments` directory.

## Usage

Run the transcription script:

```
python src/02-translate-audio.py
```

The script will:
1. Process all MP4 files in the segments directory
2. Save the transcriptions as JSON files in the `output/transcripts` directory
3. Skip files that have already been transcribed

## Output

Transcription results are saved as JSON files in the `output/transcripts` directory, with the same base name as the source audio file.

# azure-ai-audio-transcribe 