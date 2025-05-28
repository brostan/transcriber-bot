# transcribe.py
import os
import sys
import argparse
from openai import OpenAI
from config import OPENAI_API_KEY


def transcribe_audio(input_path: str, output_path: str):
    """
    Transcribes an MP3 audio file to text using OpenAI's Whisper API and saves the result.

    Args:
        input_path (str): Path to the input MP3 file.
        output_path (str): Path to the output text file.
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Read audio and call Whisper API
    with open(input_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    # Extract transcription
    text = response.text

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

    print(f"Transcription saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe an MP3 file to text using OpenAI Whisper API"
    )
    parser.add_argument(
        "input",
        help="Path to the input MP3 file (e.g., audio.mp3)"
    )
    parser.add_argument(
        "output",
        help="Path to the output TXT file (e.g., transcript.txt)"
    )
    args = parser.parse_args()

    # Ensure API key is available
    if not OPENAI_API_KEY:
        print(
            "Error: OPENAI_API_KEY is missing.\n"
            "Create a .env file in project root with OPENAI_API_KEY=your_key"
        )
        sys.exit(1)

    transcribe_audio(args.input, args.output)


if __name__ == "__main__":
    main()

# Requirements:
#   pip install openai python-dotenv
