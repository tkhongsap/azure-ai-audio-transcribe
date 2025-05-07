# Azure AI Audio Transcription

This project provides tools for splitting and transcribing audio/video files using Azure OpenAI's GPT-4o Transcribe model.

## Features

- Split large audio/video files into smaller segments
- Transcribe audio using Azure OpenAI's advanced AI models
- Automatically skip already processed files
- Save transcriptions as structured JSON files

## Prerequisites

- Python 3.8+
- Azure OpenAI API key
- MP4 audio/video files for processing

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/tkhongsap/azure-ai-audio-transcribe.git
   cd azure-ai-audio-transcribe
   ```

2. Install the required dependencies:
   ```
   pip install requests python-dotenv
   ```

3. Create a `.env` file in the root directory using the provided template:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your Azure API key:
   ```
   AZURE_API_KEY=your_azure_api_key_here
   ```

4. Place your MP4 files in a directory of your choice.

## Usage

### Step 1: Split Audio Files (Optional)

If you have large audio/video files, you can split them into smaller segments:

```
python src/01-split-audio.py
```

The split files will be saved in the `output/[Internal] OCR Logic_segments` directory.

### Step 2: Transcribe Audio

Run the transcription script:

```
python src/02-transcribe-audio.py
```

The script will:
1. Process all MP4 files in the segments directory
2. Save the transcriptions as JSON files in the `output/transcripts` directory
3. Skip files that have already been transcribed

## Output

Transcription results are saved as JSON files in the `output/transcripts` directory, with the same base name as the source audio file.

## License

This project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 