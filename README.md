# Persona 5 // Text Purge

Persona 5 Text Purge is a desktop utility built as an experimental prototype for UI making and interface design training, exploring the high-contrast aesthetic of Persona 5 while providing a fast tool for targeted text sanitization.

When working with long documents, meeting transcripts, code dumps, or messy OCR exports, unwanted boilerplate, repeated phrases, or bad paragraphs clutter the content. This tool provides a dedicated 3-panel workspace to target and purge specific text blocks instantly.

## Features

* Persona 5 Interface: High-contrast red, black, and white cards with angled geometry and custom styling.
* UI Design Prototype: Built as a hands-on project for game UI reconstruction and desktop frontend practice.
* 3-Panel Workflow: Dedicated areas for original source text, target deletion string, and cleansed output.
* Live Radar Detection: Real-time search counter tracking matches and character counts as you type.
* Clean Spacing Normalization: Eliminates excess empty lines left behind by purged paragraphs.
* Direct Windows Clipboard: Fast clipboard operations without external dependencies.
* Global Shortcuts: Quick keyboard triggers with Ctrl+Enter to execute purge and Ctrl+Shift+C to copy result.
* Dual Engine Support: Primary pywebview interface with an automatic Tkinter fallback.

## Installation

### Standalone Executable (Recommended)

No Python installation or setup required.

1. Download Persona5-TextPurge.exe from the Releases page.
2. Run the executable directly on Windows.

### Running From Source

Prerequisites: Python 3.10+ on Windows.

1. Clone this repository:
   git clone https://github.com/Velgoh/Persona5-TextPurge.git
2. Install dependencies:
   pip install pywebview
3. Launch the app:
   python remove_paragraph.py
   Or double click Launch Persona 5 Text Purge.bat.

## Usage

* Box 1 (Original Text): Paste your raw document, transcript, or source text.
* Box 2 (Text to Delete): Type or paste the exact phrase, paragraph, or recurring boilerplate to remove. The radar badge displays live match counts.
* Execute Purge: Click Execute Purge or press Ctrl+Enter to strip out all occurrences and normalize paragraph spacing.
* Box 3 (Cleansed Result): Review the sanitized output with character removal statistics.
* Copy Result: Click Copy Result to Clipboard or press Ctrl+Shift+C to copy the output.

## License

This project is open source and licensed under the [MIT License](LICENSE). You are free to use, modify, distribute, and build upon this software, provided that proper credit and attribution are given to the original author (Velgoh).

---
*Glory to mankind.*
