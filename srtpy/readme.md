# SRT AI Translator - Python Implementation

This Python script provides a standalone implementation of the SRT AI Translator functionality, allowing you to translate SRT subtitle files to any language using AI.

## Overview

The Python implementation replicates the core functionality of the original JavaScript/TypeScript project, focusing on the translation capabilities without the UI components. It uses Google's Gemini API to provide accurate and natural-sounding translations for SRT subtitle files.

## Features

- Parse and process SRT files
- Group segments to respect token limits
- Translate text using Google's Gemini AI
- Maintain original SRT structure and timestamps
- Handle retry logic for API failures
- Support command-line usage

## Prerequisites

- Python 3.6+
- A Gemini AI API Key (get one from [Google AI Studio](https://aistudio.google.com/))

## Installation

1. Install the required dependencies:
   ```bash
   pip install google-generativeai python-dotenv
   ```

2. Create a `.env.local` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Command Line

```bash
python srt_translator.py path/to/subtitles.srt "Spanish"
```

You can also specify an output file:

```bash
python srt_translator.py path/to/subtitles.srt "French" -o translated_subtitles.srt
```

### In Your Code

```python
from srt_translator import translate_srt_file

# Basic usage
translated_content = translate_srt_file("subtitles.srt", "German", "output.srt")

# Or without specifying output (returns translated content as string)
translated_content = translate_srt_file("subtitles.srt", "Italian")
```

## How It Works

1. **Parsing**: The script reads and parses the SRT file into segments.
2. **Grouping**: Segments are grouped to respect token limits for the AI model.
3. **Translation**: Each group is sent to the Gemini API for translation.
4. **Reconstruction**: The translated content is reconstructed into proper SRT format, maintaining the original timestamps.

## Implementation Details

The implementation includes:

- `Segment` class to represent SRT segments
- Functions for parsing and grouping segments
- Translation function using Google's Gemini API
- SRT reconstruction logic
- Command-line interface with argparse

## Error Handling

The script includes retry logic for API failures and proper error messages for common issues like missing API keys or file access problems.

## Output

By default, the script creates an output file with the format `filename.language.srt` if no output path is specified. The translated content is also returned as a string from the main function.
