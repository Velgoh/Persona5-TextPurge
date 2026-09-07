# Persona 5 // Text Purge

Persona 5 Text Purge is a lightweight desktop utility built as an experimental prototype for UI making and interface design training, exploring game UI aesthetics inspired by Persona 5 while solving the everyday problem of messy text formatting.

When copying text out of PDFs, research papers, chat logs, or code editors, awkward line breaks, erratic spacing, and fragmented sentences frequently corrupt the text. This utility provides an instant interface to clean, reformat, and sanitize paragraphs with a single keystroke.

## Features

* Persona 5 Aesthetic: High-contrast red and black panels, skewed geometry, custom animations, and audio cues.
* UI Design Prototype: Experimental project focused on game interface recreation and desktop UI styling.
* Triple Box Workspace: Side-by-side layout featuring raw input, live preview, and finalized sanitized text.
* Instant Paragraph Purge: Strips unwanted line breaks, normalizes spaces, and restores smooth sentence flow.
* Direct Windows Clipboard: Native Win32 clipboard integration for immediate copying without external dependencies.
* Quick Keyboard Shortcuts: Execute purge instantly with Ctrl+Enter and copy results with Ctrl+Shift+C.
* Dual Interface Engine: Modern pywebview interface with an automatic lightweight Tkinter fallback.

## Installation

### Standalone Executable (Recommended)

No Python installation or configuration required.

1. Download Persona5-TextPurge.exe from the Releases page.
2. Run the executable directly on Windows.

### Running From Source

Prerequisites: Python 3.10+ on Windows.

1. Clone or download this repository:
   git clone https://github.com/Velgoh/Persona5-TextPurge.git
2. Install pywebview:
   pip install pywebview
3. Run the script:
   python remove_paragraph.py
   Or double click Launch Persona 5 Text Purge.bat.

## Usage

* Input Box: Paste messy text containing unwanted breaks or awkward formatting.
* Execute Purge: Click Execute (or press Ctrl+Enter) to sanitize the text into clean paragraphs.
* Copy Output: Inspect the sanitized output in the preview and click Copy (or press Ctrl+Shift+C) to copy the text to your clipboard.

## License

This project is open source and licensed under the [MIT License](LICENSE). You are free to use, modify, distribute, and build upon this software, provided that proper credit and attribution are given to the original author (Velgoh).

---
*Glory to mankind.*
