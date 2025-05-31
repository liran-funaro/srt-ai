#!/usr/bin/env python3
import os
import re
import time
import argparse
from typing import List, Dict, Any, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv('.env.local')


# Define types similar to TypeScript
class Segment:
    def __init__(self, id: int, timestamp: str, text: str):
        self.id = id
        self.timestamp = timestamp
        self.text = text


def parse_segment(text: str) -> Segment:
    """Parse a segment from SRT format."""
    lines = re.split(r'\r\n|\n', text)
    id_str = lines[0]
    timestamp = lines[1]
    content = " ".join(lines[2:])

    try:
        id_num = int(id_str)
    except ValueError:
        id_num = 0

    return Segment(id_num, timestamp, content)


def group_segments_by_token_length(segments: List[Segment], max_tokens: int) -> List[List[Segment]]:
    """Group segments to not exceed max_tokens."""
    groups = []
    current_group = []
    current_group_token_count = 0

    # Simple token estimation (not as accurate as tiktoken but works for this purpose)
    def estimate_tokens(text: str) -> int:
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4 + 1

    for segment in segments:
        segment_token_count = estimate_tokens(segment.text)

        if current_group_token_count + segment_token_count <= max_tokens:
            current_group.append(segment)
            current_group_token_count += segment_token_count + 1  # +1 for delimiter
        else:
            groups.append(current_group)
            current_group = [segment]
            current_group_token_count = segment_token_count

    if current_group:
        groups.append(current_group)

    return groups


def retrieve_translation(text: str, language: str, api_key: str) -> str:
    """Translate text using Google Gemini API."""
    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Set up the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    retries = 3
    while retries > 0:
        try:
            response = model.generate_content([
                {
                    "role": "system",
                    "parts": [
                        "You are an experienced semantic translator, specialized in creating SRT files. Separate translation segments with the '|' symbol"]
                },
                {
                    "role": "user",
                    "parts": [f"Translate this to {language}: {text}"]
                }
            ])

            return response.text
        except Exception as e:
            print(f"Translation error: {e}")
            if retries > 1:
                print("Retrying translation...")
                time.sleep(1)
                retries -= 1
                continue
            raise e

    return ""


def translate_srt_file(file_path: str, target_language: str, output_path: str = None) -> str:
    """
    Translate an SRT file to the target language using AI.
    
    Args:
        file_path: Path to the SRT file
        target_language: Language to translate to
        output_path: Path to save the translated file (optional)
        
    Returns:
        The translated SRT content as a string
    """
    # Get API key from environment
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    # Read the SRT file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse segments
    raw_segments = re.split(r'\r\n\r\n|\n\n', content)
    segments = [parse_segment(seg) for seg in raw_segments if seg.strip()]

    # Group segments to respect token limits
    MAX_TOKENS_IN_SEGMENT = 700
    groups = group_segments_by_token_length(segments, MAX_TOKENS_IN_SEGMENT)

    translated_content = []
    current_index = 0

    # Process each group
    for group in groups:
        # Join segment texts with | delimiter
        text = "|".join([segment.text for segment in group])

        # Get translation
        translated_text = retrieve_translation(text, target_language, api_key)
        if not translated_text:
            continue

        # Split translated text back into segments
        translated_segments = translated_text.split("|")

        # Reconstruct SRT format with original timestamps
        for segment in translated_segments:
            if segment.strip():
                current_index += 1
                original_segment = segments[current_index - 1] if current_index <= len(segments) else None
                timestamp = original_segment.timestamp if original_segment else ""

                srt_block = f"{current_index}\n{timestamp}\n{segment.strip()}\n\n"
                translated_content.append(srt_block)

    # Join all translated segments
    result = "".join(translated_content)

    # Save to output file if specified
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate SRT files using AI')
    parser.add_argument('file', help='Path to the SRT file')
    parser.add_argument('language', help='Target language for translation')
    parser.add_argument('-o', '--output', help='Output file path (optional)')

    args = parser.parse_args()

    output_path = args.output
    if not output_path:
        # Create default output path by adding language code before extension
        base, ext = os.path.splitext(args.file)
        output_path = f"{base}.{args.language}{ext}"

    result = translate_srt_file(args.file, args.language, output_path)
    print(f"Translation completed and saved to {output_path}")
