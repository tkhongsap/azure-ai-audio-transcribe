import os
import sys
import subprocess
from pathlib import Path


def get_media_duration(file_path):
    """Get the duration of a media file using ffmpeg"""
    cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', 
        str(file_path)
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error getting duration: {result.stderr}")
            return None
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error running ffprobe: {e}")
        return None


def split_media_file(file_path, output_dir, num_segments=10):
    """
    Split a video or audio file into equal segments using ffmpeg
    
    Args:
        file_path (str): Path to the media file
        output_dir (Path): Directory to save output files
        num_segments (int): Number of segments to split the file into
    """
    file_path = Path(file_path)
    file_name = file_path.stem
    file_ext = file_path.suffix.lower()
    
    # Determine if it's a video or audio file
    is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    is_audio = file_ext in ['.mp3', '.wav', '.aac', '.ogg', '.flac']
    
    if not (is_video or is_audio):
        print(f"Unsupported file format: {file_ext}")
        return
    
    # Create output subdirectory for this specific file
    file_output_dir = output_dir / f"{file_name}_segments"
    os.makedirs(file_output_dir, exist_ok=True)
    
    # Get the duration of the media file
    duration = get_media_duration(file_path)
    if not duration:
        print(f"Failed to get duration for {file_path}")
        return
    
    # Calculate segment duration
    segment_duration = duration / num_segments
    
    print(f"File: {file_path}")
    print(f"Total duration: {duration:.2f} seconds")
    print(f"Splitting into {num_segments} segments of {segment_duration:.2f} seconds each")
    
    # Split the file into segments
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, duration)  # Ensure we don't exceed the file duration
        
        # Define output filename
        output_name = f"{file_name}_part{i+1:02d}{file_ext}"
        output_path = file_output_dir / output_name
        
        print(f"Creating segment {i+1}/{num_segments}: {start_time:.2f}s to {end_time:.2f}s -> {output_name}")
        
        # Set up the FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(file_path),
            '-ss', str(start_time),
            '-to', str(end_time),
            '-c', 'copy',  # Use copy codec for faster processing
            '-y',  # Overwrite output files
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"Error creating segment {i+1}: {result.stderr}")
        except Exception as e:
            print(f"Error running FFmpeg for segment {i+1}: {e}")
    
    print(f"All segments saved to: {file_output_dir}")


def main():
    # Get directory containing this script
    script_dir = Path(__file__).parent.parent
    
    # Path to the vdo directory
    vdo_dir = script_dir / "vdo"
    
    # Path to output directory
    output_dir = script_dir / "output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if not vdo_dir.exists():
        print(f"Error: Directory '{vdo_dir}' not found")
        sys.exit(1)
    
    # List all files in the vdo directory
    media_files = []
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.mp3', '.wav', '.aac', '.ogg', '.flac']:
        media_files.extend(list(vdo_dir.glob(f"*{ext}")))
    
    if not media_files:
        print(f"No media files found in {vdo_dir}")
        sys.exit(1)
    
    # Print found files
    print(f"Found {len(media_files)} media files:")
    for i, file in enumerate(media_files, 1):
        print(f"{i}. {file.name}")
    
    print(f"\nOutput will be saved to: {output_dir}")
    
    # Choose to process all files or select one
    choice = input("\nEnter the number of the file to process, or 'all' to process all files: ")
    
    if choice.lower() == 'all':
        # Process all files
        for file in media_files:
            split_media_file(file, output_dir)
    else:
        try:
            # Process selected file
            index = int(choice) - 1
            if 0 <= index < len(media_files):
                split_media_file(media_files[index], output_dir)
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(media_files)}")
        except ValueError:
            print("Invalid input. Please enter a number or 'all'")


if __name__ == "__main__":
    main()
