#!/usr/bin/env python3
"""
================================================================================
 PERSONA 5: THE PHANTOM TEXT PURGE // ALL-OUT REMOVER
 High-Fidelity Metaverse Edition
 Standalone & Portable Desktop Text Sanitizer
================================================================================
"""

import sys
import os
import re
import json
import time
import ctypes

# Ensure UTF-8 output in Windows terminals to prevent charmap/cp1252 encoding crashes
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ──────────────────────────────────────────────────────────────────────────────
# Windows Native Clipboard Support (64-bit / 32-bit Safe with Proper Types)
# ──────────────────────────────────────────────────────────────────────────────
def _init_win32_clipboard():
    """Configures ctypes argtypes and restypes for 64-bit Windows safety."""
    if sys.platform != "win32":
        return None, None
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        # kernel32 declarations
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.restype = ctypes.c_bool
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

        # user32 declarations
        user32.OpenClipboard.restype = ctypes.c_bool
        user32.OpenClipboard.argtypes = [ctypes.c_void_p]
        user32.CloseClipboard.restype = ctypes.c_bool
        user32.CloseClipboard.argtypes = []
        user32.EmptyClipboard.restype = ctypes.c_bool
        user32.EmptyClipboard.argtypes = []
        user32.GetClipboardData.restype = ctypes.c_void_p
        user32.GetClipboardData.argtypes = [ctypes.c_uint]
        user32.SetClipboardData.restype = ctypes.c_void_p
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

        return user32, kernel32
    except Exception:
        return None, None


_USER32, _KERNEL32 = _init_win32_clipboard()


def set_windows_clipboard(text: str) -> bool:
    """Copies Unicode text to the Windows system clipboard safely."""
    if not _USER32 or not _KERNEL32:
        return False
    try:
        # Retry up to 5 times in case another app holds the clipboard
        opened = False
        for _ in range(5):
            if _USER32.OpenClipboard(None):
                opened = True
                break
            time.sleep(0.02)
        if not opened:
            return False

        try:
            _USER32.EmptyClipboard()
            data = text.encode("utf-16le") + b"\x00\x00"
            h_mem = _KERNEL32.GlobalAlloc(0x0002, len(data))  # GMEM_MOVEABLE = 0x0002
            if not h_mem:
                return False

            p_mem = _KERNEL32.GlobalLock(h_mem)
            if not p_mem:
                return False

            ctypes.memmove(p_mem, data, len(data))
            _KERNEL32.GlobalUnlock(h_mem)

            # CF_UNICODETEXT = 13
            res = _USER32.SetClipboardData(13, h_mem)
            return bool(res)
        finally:
            _USER32.CloseClipboard()
    except Exception:
        return False


def get_windows_clipboard() -> str:
    """Reads Unicode text from the Windows system clipboard safely."""
    if not _USER32 or not _KERNEL32:
        return ""
    try:
        opened = False
        for _ in range(5):
            if _USER32.OpenClipboard(None):
                opened = True
                break
            time.sleep(0.02)
        if not opened:
            return ""

        try:
            # CF_UNICODETEXT = 13
            h_mem = _USER32.GetClipboardData(13)
            if not h_mem:
                return ""

            p_mem = _KERNEL32.GlobalLock(h_mem)
            if not p_mem:
                return ""

            try:
                return ctypes.wstring_at(p_mem)
            finally:
                _KERNEL32.GlobalUnlock(h_mem)
        finally:
            _USER32.CloseClipboard()
    except Exception:
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# Core String Removal & Newline Normalization Logic
# ──────────────────────────────────────────────────────────────────────────────
def purge_text_logic(original: str, target: str) -> dict:
    """
    Core string removal algorithm:
    1. Validates non-empty inputs
    2. Exact character-for-character match count (with CRLF/LF normalization fallback)
    3. Literal string replacement
    4. Collapse 3+ consecutive newlines to 2 (supporting both CRLF and LF)
    5. Returns statistics and Persona 5 themed status message
    """
    if not original:
        return {
            "success": False,
            "error": "empty_original",
            "message": "⚠️ Original text is empty! Paste your target document in Box ①."
        }
    if not target:
        return {
            "success": False,
            "error": "empty_target",
            "message": "⚠️ Target phrase is empty! Paste the exact text to delete in Box ②."
        }

    # Direct literal match first
    if target in original:
        count = original.count(target)
        cleaned = original.replace(target, "")
    else:
        # Check if line endings differed between sources (e.g. CRLF vs LF)
        norm_orig = original.replace("\r\n", "\n")
        norm_target = target.replace("\r\n", "\n")
        if norm_target in norm_orig:
            count = norm_orig.count(norm_target)
            cleaned = norm_orig.replace(norm_target, "")
            # Preserve CRLF if original exclusively used CRLF
            if "\r\n" in original and "\r" not in cleaned:
                cleaned = cleaned.replace("\n", "\r\n")
        else:
            return {
                "success": False,
                "error": "not_found",
                "count": 0,
                "message": "❌ Target phrase not found! Ensure character-for-character match."
            }

    # Collapse 3 or more consecutive newlines down to 2 (handles both CRLF and LF)
    cleaned = re.sub(r"(?:\r\n){3,}", "\r\n\r\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    removed_chars = len(original) - len(cleaned)

    return {
        "success": True,
        "cleaned": cleaned,
        "count": count,
        "removed_chars": removed_chars,
        "message": f"★ MISSION ACCOMPLISHED! Eradicated {count} occurrence(s) ({removed_chars:,} chars removed)!"
    }


# ──────────────────────────────────────────────────────────────────────────────
# Persona 5 Desktop Webview HTML / CSS / JS Application
# ──────────────────────────────────────────────────────────────────────────────
PERSONA_5_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark">
<title>PERSONA 5 // TEXT PURGE</title>
<style>
/* ── PERSONA 5 DESIGN SYSTEM & THEME TOKENS ──────────────────────────────── */
*, *::before, *::after {
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  outline: none;
}

:root {
  color-scheme: dark !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
  --p5-red: #e60012;
  --p5-red-dark: #8c000b;
  --p5-red-bright: #ff1a2d;
  --p5-black: #0a0a0c;
  --p5-black-card: #131316;
  --p5-black-input: #17171c;
  --p5-white: #ffffff;
  --p5-yellow: #ffe600;
  --p5-green: #00e676;
  --p5-gray-border: #2c2c34;
  --p5-gray-muted: #888892;
  --p5-font-display: Impact, "Arial Black", "Segoe UI Black", "Haettenschweiler", sans-serif;
  --p5-font-mono: Consolas, "Cascadia Code", "Courier New", monospace;
  --p5-font-ui: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
  --p5-skew: -4.5deg;
  --p5-skew-counter: 4.5deg;
}

@media (forced-colors: active), (-ms-high-contrast: active) {
  :root, *, *::before, *::after, button, textarea, input, select {
    forced-color-adjust: none !important;
    -ms-high-contrast-adjust: none !important;
  }
  body {
    background-color: #070709 !important;
    color: #ffffff !important;
  }
  .calling-card-header, .p5-card, .comic-status-bar {
    background-color: #131316 !important;
    border-color: #000000 !important;
  }
  .calling-card-header {
    border-left: 8px solid #e60012 !important;
  }
  .badge-take {
    background-color: #000000 !important;
    color: #ffffff !important;
  }
  .badge-your {
    background-color: #e60012 !important;
    color: #ffffff !important;
  }
  .badge-text {
    background-color: #ffffff !important;
    color: #000000 !important;
  }
  .header-sub, .all-out-sub, .sfx-status-text {
    color: #ffe600 !important;
  }
  .tag-orig {
    background-color: #ffffff !important;
    color: #000000 !important;
  }
  .tag-target {
    background-color: #e60012 !important;
    color: #ffffff !important;
  }
  .tag-result {
    background-color: #ffe600 !important;
    color: #000000 !important;
  }
  .p5-textarea {
    background-color: #17171c !important;
    color: #ffffff !important;
    border-color: #222222 !important;
  }
  #box-result {
    background-color: #0b130e !important;
    color: #bdfccb !important;
  }
  .btn-all-out {
    background-color: #e60012 !important;
    color: #ffffff !important;
  }
  .all-out-title {
    color: #ffffff !important;
  }
  .btn-copy-result {
    background-color: #ffe600 !important;
    color: #000000 !important;
  }
  .sfx-toggle-btn, .mini-btn, .stat-pill {
    background-color: #000000 !important;
    color: #ffffff !important;
  }
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  color-scheme: dark !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
  background-color: #070709 !important;
  background-color: var(--p5-black, #070709) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  font-family: var(--p5-font-ui, "Segoe UI", sans-serif);
  user-select: none;
}

/* Halftone dot pattern backdrop with diagonal crimson slash */
body {
  background-color: #070709 !important;
  background-image:
    radial-gradient(circle, rgba(255, 255, 255, 0.08) 1.2px, transparent 1.2px),
    linear-gradient(135deg, rgba(230, 0, 18, 0.14) 0%, transparent 42%),
    repeating-linear-gradient(-45deg, rgba(0,0,0,0.4) 0, rgba(0,0,0,0.4) 12px, transparent 12px, transparent 24px) !important;
  background-size: 16px 16px, 100% 100%, 100% 100%;
}

::selection {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
}

/* ── APP CONTAINER & LAYOUT ──────────────────────────────────────────────── */
#app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 12px 18px;
  gap: 10px;
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
  transition: transform 0.05s ease;
}

/* Screen Shake on All-Out Attack */
.shake-effect {
  animation: p5Shake 0.4s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes p5Shake {
  10%, 90% { transform: translate3d(-3px, 0, 0) rotate(-0.5deg); }
  20%, 80% { transform: translate3d(4px, 0, 0) rotate(0.5deg); }
  30%, 50%, 70% { transform: translate3d(-5px, 0, 0) rotate(-1deg); }
  40%, 60% { transform: translate3d(5px, 0, 0) rotate(1deg); }
}

/* ── HEADER / "TAKE YOUR HEART" CALLING CARD BANNER ──────────────────────── */
.calling-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #131316 !important;
  background: var(--p5-black-card, #131316) !important;
  border: 3px solid #000000 !important;
  box-shadow: 6px 6px 0px #000000 !important;
  padding: 8px 16px;
  transform: skew(var(--p5-skew, -4.5deg));
  position: relative;
  z-index: 10;
  border-left: 8px solid #e60012 !important;
  border-left: 8px solid var(--p5-red, #e60012) !important;
  flex-shrink: 0;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  transform: skew(var(--p5-skew-counter, 4.5deg));
}

.ransom-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ransom-badge {
  display: inline-block;
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 22px;
  letter-spacing: 1px;
  padding: 2px 8px;
  font-weight: 900;
  border: 2px solid #000000 !important;
  box-shadow: 3px 3px 0px #000000 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.badge-take {
  background: #000000 !important;
  color: #ffffff !important;
  transform: rotate(-3deg);
}

.badge-your {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  transform: rotate(2deg);
}

.badge-text {
  background: #ffffff !important;
  color: #000000 !important;
  transform: rotate(-2deg);
}

.header-sub {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 13px;
  letter-spacing: 1.5px;
  color: #ffe600 !important;
  color: var(--p5-yellow, #ffe600) !important;
  text-transform: uppercase;
  margin-left: 8px;
  text-shadow: 2px 2px 0px #000000 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  transform: skew(var(--p5-skew-counter, 4.5deg));
}

.sfx-toggle-btn {
  background: #000000 !important;
  color: #ffffff !important;
  border: 2px solid #e60012 !important;
  border: 2px solid var(--p5-red, #e60012) !important;
  box-shadow: 3px 3px 0px #000000 !important;
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 13px;
  letter-spacing: 1px;
  padding: 5px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.sfx-toggle-btn:hover {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 4px 4px 0px #000000 !important;
}

.sfx-status-text {
  color: #ffe600 !important;
  color: var(--p5-yellow, #ffe600) !important;
}

/* ── PANELS SHARED STYLING ───────────────────────────────────────────────── */
.p5-card {
  display: flex;
  flex-direction: column;
  background: #131316 !important;
  background: var(--p5-black-card, #131316) !important;
  border: 2px solid #000000 !important;
  box-shadow: 5px 5px 0px #000000 !important;
  transform: skew(var(--p5-skew, -4.5deg));
  position: relative;
  padding: 8px 12px;
  min-height: 0;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.card-orig {
  flex: 1.3 1 120px;
}

.card-target {
  flex: 0.85 1 80px;
}

.card-result {
  flex: 1.3 1 120px;
}

.p5-card-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  transform: skew(var(--p5-skew-counter, 4.5deg));
  gap: 6px;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.panel-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 14px;
  letter-spacing: 1.2px;
  padding: 3px 10px;
  border: 2px solid #000000 !important;
  box-shadow: 3px 3px 0px #000000 !important;
  font-weight: 900;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.tag-orig {
  background: #ffffff !important;
  color: #000000 !important;
  transform: rotate(-1.5deg);
}

.tag-target {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  transform: rotate(1.5deg);
}

.tag-result {
  background: #ffe600 !important;
  background: var(--p5-yellow, #ffe600) !important;
  color: #000000 !important;
  transform: rotate(-1.2deg);
}

.panel-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-pill {
  font-family: var(--p5-font-mono, Consolas, monospace);
  font-size: 11px;
  color: #888892 !important;
  color: var(--p5-gray-muted, #888892) !important;
  background: #000000 !important;
  padding: 3px 8px;
  border: 1px solid #333333 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.mini-btn {
  background: #000000 !important;
  color: #ffffff !important;
  border: 1px solid #444444 !important;
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 11px;
  padding: 3px 8px;
  cursor: pointer;
  transition: all 0.1s;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.mini-btn:hover {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  border-color: #000000 !important;
  color: #ffffff !important;
}

/* ── TEXTAREA STYLES ─────────────────────────────────────────────────────── */
.p5-textarea {
  width: 100%;
  flex: 1 1 auto;
  background-color: #17171c !important;
  background: #17171c !important;
  background: var(--p5-black-input, #17171c) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  border: 2px solid #222222 !important;
  font-family: var(--p5-font-mono, Consolas, monospace);
  font-size: 13px;
  line-height: 1.45;
  padding: 8px 10px;
  resize: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  user-select: text;
  min-height: 50px;
  color-scheme: dark !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.p5-textarea:focus {
  border-color: #e60012 !important;
  border-color: var(--p5-red, #e60012) !important;
  box-shadow: inset 0 0 8px rgba(230, 0, 18, 0.4) !important;
}

.p5-textarea::placeholder {
  color: #6e6e7c !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

/* Custom Persona 5 Scrollbar */
.p5-textarea::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.p5-textarea::-webkit-scrollbar-track {
  background: #08080a !important;
}

.p5-textarea::-webkit-scrollbar-thumb {
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  border: 1px solid #000000 !important;
}

.p5-textarea::-webkit-scrollbar-thumb:hover {
  background: #ff1a2d !important;
  background: var(--p5-red-bright, #ff1a2d) !important;
}

#box-result {
  background-color: #0b130e !important;
  background: #0b130e !important;
  color: #bdfccb !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

#box-result::placeholder {
  color: #3b5e43 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

/* ── LIVE TARGET OCCURRENCE RADAR ────────────────────────────────────────── */
.radar-badge {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 12px;
  letter-spacing: 1px;
  padding: 3px 8px;
  border: 2px solid #000000 !important;
  box-shadow: 2px 2px 0px #000000 !important;
  font-weight: 900;
  transition: all 0.15s ease;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.radar-waiting {
  background: #222222 !important;
  color: #888888 !important;
}

.radar-found {
  background: #ffe600 !important;
  background: var(--p5-yellow, #ffe600) !important;
  color: #000000 !important;
  animation: pulseYellow 1s infinite alternate;
}

.radar-zero {
  background: #3a1111 !important;
  color: #ff9999 !important;
  border-color: #e60012 !important;
  border-color: var(--p5-red, #e60012) !important;
}

@keyframes pulseYellow {
  0% { transform: scale(1); }
  100% { transform: scale(1.04); }
}

/* ── ACTION SECTION: ALL-OUT ATTACK BUTTON + COMIC STATUS ─────────────────── */
.action-container {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 2px 0;
  transform: skew(var(--p5-skew, -4.5deg));
  flex-shrink: 0;
}

.btn-all-out {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #e60012 !important;
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  border: 3px solid #000000 !important;
  box-shadow: 6px 6px 0px #000000 !important;
  padding: 9px 24px;
  cursor: pointer;
  position: relative;
  transition: all 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
  color-scheme: dark !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.btn-all-out:hover {
  background: #ff1a2d !important;
  background: var(--p5-red-bright, #ff1a2d) !important;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 8px 8px 0px #000000 !important;
}

.btn-all-out:active {
  transform: translate(4px, 4px) scale(0.98);
  box-shadow: 2px 2px 0px #000000 !important;
}

.all-out-title {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 19px;
  letter-spacing: 2px;
  color: #ffffff !important;
  color: var(--p5-white, #ffffff) !important;
  text-shadow: 2px 2px 0px #000000 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.all-out-sub {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 11px;
  letter-spacing: 1.5px;
  color: #ffe600 !important;
  color: var(--p5-yellow, #ffe600) !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

/* Comic Speech Bubble / Alert Bar */
.comic-status-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #111116 !important;
  background: #111116 !important;
  border: 2px solid #000000 !important;
  box-shadow: 4px 4px 0px #000000 !important;
  padding: 9px 14px;
  position: relative;
  min-width: 0;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.status-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.status-text {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 13px;
  letter-spacing: 1px;
  color: #ffffff !important;
  transform: skew(var(--p5-skew-counter, 4.5deg));
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.status-success {
  background: #0e2413 !important;
  border-color: #00e676 !important;
  border-color: var(--p5-green, #00e676) !important;
}
.status-success .status-text {
  color: #7aff9e !important;
}

.status-error {
  background: #2d0e0e !important;
  border-color: #e60012 !important;
  border-color: var(--p5-red, #e60012) !important;
}
.status-error .status-text {
  color: #ff8585 !important;
}

/* ── COPY RESULT BUTTON ──────────────────────────────────────────────────── */
.copy-btn-container {
  margin-top: 2px;
  transform: skew(var(--p5-skew, -4.5deg));
  flex-shrink: 0;
}

.btn-copy-result {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: #ffe600 !important;
  background: #ffe600 !important;
  background: var(--p5-yellow, #ffe600) !important;
  color: #000000 !important;
  border: 3px solid #000000 !important;
  box-shadow: 5px 5px 0px #000000 !important;
  padding: 10px 16px;
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 16px;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.15s ease;
  clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
  color-scheme: dark !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.btn-copy-result:hover {
  background: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 7px 7px 0px #000000 !important;
}

.btn-copy-result:active {
  transform: translate(3px, 3px);
  box-shadow: 2px 2px 0px #000000 !important;
}

.btn-copy-copied {
  background-color: #00e676 !important;
  background: #00e676 !important;
  color: #000000 !important;
  animation: pulseGreen 0.4s alternate infinite;
}

@keyframes pulseGreen {
  from { transform: scale(1); }
  to { transform: scale(1.02); }
}

/* ── ALL-OUT ATTACK FINISHER OVERLAY ─────────────────────────────────────── */
#finisher-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.25s ease;
  overflow: hidden;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

#finisher-overlay.active {
  opacity: 1;
}

.slash-layer-1 {
  position: absolute;
  top: -20%;
  left: -20%;
  width: 140%;
  height: 38%;
  background: #e60012 !important;
  background: var(--p5-red, #e60012) !important;
  transform: rotate(-22deg) scaleX(0);
  transform-origin: left center;
  border-top: 8px solid #000000 !important;
  border-bottom: 8px solid #ffffff !important;
  box-shadow: 0 0 30px rgba(230,0,18,0.8);
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.slash-layer-2 {
  position: absolute;
  top: 45%;
  left: -20%;
  width: 140%;
  height: 25%;
  background: #ffffff !important;
  transform: rotate(-22deg) scaleX(0);
  transform-origin: right center;
  border-top: 6px solid #000000 !important;
  border-bottom: 6px solid #e60012 !important;
  border-bottom: 6px solid var(--p5-red, #e60012) !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

#finisher-overlay.active .slash-layer-1 {
  animation: slashSwipe 0.3s cubic-bezier(0.1, 0.9, 0.2, 1) forwards;
}

#finisher-overlay.active .slash-layer-2 {
  animation: slashSwipeReverse 0.3s cubic-bezier(0.1, 0.9, 0.2, 1) forwards;
}

@keyframes slashSwipe {
  0% { transform: rotate(-22deg) scaleX(0); }
  100% { transform: rotate(-22deg) scaleX(1); }
}

@keyframes slashSwipeReverse {
  0% { transform: rotate(-22deg) scaleX(0); }
  100% { transform: rotate(-22deg) scaleX(1); }
}

.finisher-stamp {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-5deg) scale(0);
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #000000 !important;
  border: 4px solid #e60012 !important;
  border: 4px solid var(--p5-red, #e60012) !important;
  box-shadow: 10px 10px 0px rgba(230,0,18,0.7);
  padding: 16px 36px;
  z-index: 10000;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

#finisher-overlay.active .finisher-stamp {
  animation: stampPop 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.05s forwards;
}

@keyframes stampPop {
  0% { transform: translate(-50%, -50%) rotate(-12deg) scale(0); }
  70% { transform: translate(-50%, -50%) rotate(-4deg) scale(1.15); }
  100% { transform: translate(-50%, -50%) rotate(-5deg) scale(1); }
}

.finisher-title {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 38px;
  letter-spacing: 4px;
  color: #ffe600 !important;
  color: var(--p5-yellow, #ffe600) !important;
  text-shadow: 3px 3px 0px #000000 !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}

.finisher-sub {
  font-family: var(--p5-font-display, Impact, sans-serif);
  font-size: 16px;
  letter-spacing: 3px;
  color: #ffffff !important;
  forced-color-adjust: none !important;
  -ms-high-contrast-adjust: none !important;
}
</style>
</head>
<body>

<!-- ALL-OUT ATTACK FINISHER OVERLAY -->
<div id="finisher-overlay">
  <div class="slash-layer-1" style="background:#e60012;"></div>
  <div class="slash-layer-2" style="background:#ffffff;border-bottom:6px solid #e60012;"></div>
  <div class="finisher-stamp" style="background:#000000;border:4px solid #e60012;">
    <div class="finisher-title" style="color:#ffe600;">★ SHOW'S OVER! ★</div>
    <div class="finisher-sub" style="color:#ffffff;">THE TEXT WAS STOLEN FROM REALITY</div>
  </div>
</div>

<div id="app-container">

  <!-- HEADER / CALLING CARD -->
  <header class="calling-card-header" style="background:#131316;border-left:8px solid #e60012;">
    <div class="header-left">
      <div class="ransom-title">
        <span class="ransom-badge badge-take" style="background:#000000;color:#ffffff;">TAKE</span>
        <span class="ransom-badge badge-your" style="background:#e60012;color:#ffffff;">YOUR</span>
        <span class="ransom-badge badge-text" style="background:#ffffff;color:#000000;">TEXT</span>
      </div>
      <div class="header-sub" style="color:#ffe600;">★ PHANTOM TEXT PURGE // ALL-OUT REMOVER ★</div>
    </div>
    <div class="header-right">
      <button id="sfx-btn" class="sfx-toggle-btn" onclick="toggleSFX()" title="Toggle Persona 5 Sound Effects" style="background:#000000;color:#ffffff;border:2px solid #e60012;">
        <span id="sfx-icon">🔊</span> SFX: <span id="sfx-status" class="sfx-status-text" style="color:#ffe600;">ON</span>
      </button>
    </div>
  </header>

  <!-- PANEL ①: ORIGINAL DOCUMENT -->
  <section class="p5-card card-orig" style="background:#131316;">
    <div class="p5-card-inner">
      <div class="panel-header">
        <div class="panel-tag tag-orig" style="background:#ffffff;color:#000000;">
          <span>★</span> ① ORIGINAL TEXT
        </div>
        <div class="panel-tools">
          <div id="stats-orig" class="stat-pill" style="background:#000000;color:#888892;border:1px solid #333333;">0 chars | 0 words</div>
          <button class="mini-btn" onclick="pasteOriginal()" title="Paste from Clipboard" style="background:#000000;color:#ffffff;border:1px solid #444444;">PASTE [📋]</button>
          <button class="mini-btn" onclick="clearOriginal()" title="Clear original text" style="background:#000000;color:#ffffff;border:1px solid #444444;">CLEAR [×]</button>
        </div>
      </div>
      <textarea id="box-original" class="p5-textarea" spellcheck="false"
        style="background-color:#17171c;color:#ffffff;"
        placeholder="Paste your full original text here…"></textarea>
    </div>
  </section>

  <!-- PANEL ②: EXACT TEXT TO DELETE -->
  <section class="p5-card card-target" style="background:#131316;">
    <div class="p5-card-inner">
      <div class="panel-header">
        <div class="panel-tag tag-target" style="background:#e60012;color:#ffffff;">
          <span>★</span> ② TEXT TO DELETE
        </div>
        <div class="panel-tools">
          <div id="radar-badge" class="radar-badge radar-waiting" style="background:#222222;color:#888888;">RADAR: WAITING</div>
          <button class="mini-btn" onclick="pasteTarget()" title="Paste from Clipboard" style="background:#000000;color:#ffffff;border:1px solid #444444;">PASTE [📋]</button>
          <button class="mini-btn" onclick="clearTarget()" title="Clear target phrase" style="background:#000000;color:#ffffff;border:1px solid #444444;">CLEAR [×]</button>
        </div>
      </div>
      <textarea id="box-target" class="p5-textarea" spellcheck="false"
        style="background-color:#17171c;color:#ffffff;"
        placeholder="Paste the exact phrase / paragraph you want deleted here…"></textarea>
    </div>
  </section>

  <!-- ACTION ZONE: ALL-OUT ATTACK BUTTON + COMIC STATUS -->
  <div class="action-container">
    <button id="btn-execute" class="btn-all-out" onclick="triggerPurge()"
      style="background-color:#e60012;color:#ffffff;"
      title="Remove exact text (Ctrl + Enter)">
      <div class="all-out-title" style="color:#ffffff;">★ EXECUTE PURGE ★</div>
      <div class="all-out-sub" style="color:#ffe600;">[ ALL-OUT ATTACK // CTRL + ENTER ]</div>
    </button>
    <div id="status-bar" class="comic-status-bar" style="background:#111116;color:#ffffff;">
      <span id="status-icon" class="status-icon">💬</span>
      <span id="status-text" class="status-text" style="color:#ffffff;">READY FOR INFILTRATION - AWAITING COMMAND</span>
    </div>
  </div>

  <!-- PANEL ③: CLEANSED RESULT -->
  <section class="p5-card card-result" style="background:#131316;">
    <div class="p5-card-inner">
      <div class="panel-header">
        <div class="panel-tag tag-result" style="background:#ffe600;color:#000000;">
          <span>★</span> ③ CLEANSED RESULT
        </div>
        <div class="panel-tools">
          <div id="stats-result" class="stat-pill" style="background:#000000;color:#888892;border:1px solid #333333;">0 chars</div>
          <button class="mini-btn" onclick="clearResult()" title="Clear result text" style="background:#000000;color:#ffffff;border:1px solid #444444;">CLEAR [×]</button>
        </div>
      </div>
      <textarea id="box-result" class="p5-textarea" readonly spellcheck="false"
        style="background-color:#0b130e;color:#bdfccb;"
        placeholder="Cleaned result will appear here after execution…"></textarea>
    </div>
  </section>

  <!-- COPY ACTION BUTTON -->
  <div class="copy-btn-container">
    <button id="btn-copy" class="btn-copy-result" onclick="copyResult()"
      style="background-color:#ffe600;color:#000000;"
      title="Copy result to clipboard (Ctrl + Shift + C)">
      <span>★</span>
      <span id="btn-copy-label">📋 COPY RESULT TO CLIPBOARD [CTRL+SHIFT+C]</span>
      <span>★</span>
    </button>
  </div>

</div>

<script>
// ─────────────────────────────────────────────────────────────────────────────
// Web Audio API: Persona 5 Real-Time Synthesizer
// ─────────────────────────────────────────────────────────────────────────────
let sfxEnabled = true;
let audioCtx = null;

try {
  const savedSFX = localStorage.getItem("p5_sfx");
  if (savedSFX !== null) {
    sfxEnabled = (savedSFX === "true");
  }
} catch(e) {}

function updateSFXUI() {
  const statusEl = document.getElementById("sfx-status");
  const iconEl = document.getElementById("sfx-icon");
  if (sfxEnabled) {
    statusEl.innerText = "ON";
    statusEl.style.color = "#ffe600";
    iconEl.innerText = "🔊";
  } else {
    statusEl.innerText = "OFF";
    statusEl.style.color = "#888892";
    iconEl.innerText = "🔇";
  }
}

function toggleSFX() {
  sfxEnabled = !sfxEnabled;
  try {
    localStorage.setItem("p5_sfx", sfxEnabled.toString());
  } catch(e) {}
  updateSFXUI();
  if (sfxEnabled) {
    playHover();
  }
}

function getAudioContext() {
  if (!audioCtx) {
    try {
      var AudioCtor = window.AudioContext || window.webkitAudioContext;
      if (AudioCtor) {
        audioCtx = new AudioCtor();
      }
    } catch(e) {
      audioCtx = null;
    }
  }
  if (audioCtx && audioCtx.state === "suspended") {
    try {
      audioCtx.resume().catch(() => {});
    } catch(e) {}
  }
  return audioCtx;
}

// User interaction gesture unlock listener
function unlockAudio() {
  try {
    getAudioContext();
  } catch(e) {}
  try {
    window.removeEventListener("pointerdown", unlockAudio);
    window.removeEventListener("keydown", unlockAudio);
  } catch(e) {}
}
window.addEventListener("pointerdown", unlockAudio, { once: true });
window.addEventListener("keydown", unlockAudio, { once: true });

// 1. Menu Hover SFX: Snappy high blip
function playHover() {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    if (ctx.state !== "running") return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(850, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1450, ctx.currentTime + 0.035);
    gain.gain.setValueAtTime(0.06, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.035);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.04);
  } catch(e) {}
}

// 2. Select / Click SFX
function playClick() {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(620, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(920, ctx.currentTime + 0.06);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.06);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.07);
  } catch(e) {}
}

// 3. All-Out Attack Slash Impact SFX
function playSlashImpact() {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;

    // Sub-bass hit
    const sub = ctx.createOscillator();
    const subGain = ctx.createGain();
    sub.type = "sine";
    sub.frequency.setValueAtTime(140, now);
    sub.frequency.exponentialRampToValueAtTime(35, now + 0.35);
    subGain.gain.setValueAtTime(0.35, now);
    subGain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
    sub.connect(subGain);
    subGain.connect(ctx.destination);
    sub.start(now);
    sub.stop(now + 0.36);

    // Distorted blade slash
    const saw = ctx.createOscillator();
    const sawGain = ctx.createGain();
    saw.type = "sawtooth";
    saw.frequency.setValueAtTime(480, now);
    saw.frequency.exponentialRampToValueAtTime(55, now + 0.25);
    sawGain.gain.setValueAtTime(0.25, now);
    sawGain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
    saw.connect(sawGain);
    sawGain.connect(ctx.destination);
    saw.start(now);
    saw.stop(now + 0.26);

    // Noise whoosh burst
    const bufferSize = Math.floor(ctx.sampleRate * 0.25);
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const filter = ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(3200, now);
    filter.frequency.exponentialRampToValueAtTime(250, now + 0.25);
    filter.Q.value = 2.5;

    const noiseGain = ctx.createGain();
    noiseGain.gain.setValueAtTime(0.28, now);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

    noise.connect(filter);
    filter.connect(noiseGain);
    noiseGain.connect(ctx.destination);
    noise.start(now);
    noise.stop(now + 0.26);
  } catch(e) {}
}

// 4. Victory Fanfare Chime (Copy Result)
function playVictoryChime() {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    const notes = [622.25, 783.99, 932.33, 1244.51]; // Eb5, G5, Bb5, Eb6
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const start = now + idx * 0.065;
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, start);
      gain.gain.setValueAtTime(0.18, start);
      gain.gain.exponentialRampToValueAtTime(0.001, start + 0.28);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start);
      osc.stop(start + 0.3);
    });
  } catch(e) {}
}

// 5. Error Buzz SFX
function playErrorBuzz() {
  if (!sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    [0, 0.11].forEach(delay => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(140, now + delay);
      gain.gain.setValueAtTime(0.16, now + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + delay);
      osc.stop(now + delay + 0.09);
    });
  } catch(e) {}
}

// ─────────────────────────────────────────────────────────────────────────────
// UI Logic, Live Occurrence Radar, & Execution
// ─────────────────────────────────────────────────────────────────────────────
const boxOrig = document.getElementById("box-original");
const boxTarget = document.getElementById("box-target");
const boxResult = document.getElementById("box-result");
const statsOrig = document.getElementById("stats-orig");
const statsResult = document.getElementById("stats-result");
const radarBadge = document.getElementById("radar-badge");
const statusBar = document.getElementById("status-bar");
const statusText = document.getElementById("status-text");
const statusIcon = document.getElementById("status-icon");
const finisherOverlay = document.getElementById("finisher-overlay");
const appContainer = document.getElementById("app-container");
const btnCopy = document.getElementById("btn-copy");
const btnCopyLabel = document.getElementById("btn-copy-label");

function setStatus(msg, type = "idle", icon = "💬") {
  statusBar.className = "comic-status-bar";
  if (type === "success") {
    statusBar.classList.add("status-success");
    statusBar.style.backgroundColor = "#0e2413";
    statusBar.style.borderColor = "#00e676";
    statusText.style.color = "#7aff9e";
  } else if (type === "error") {
    statusBar.classList.add("status-error");
    statusBar.style.backgroundColor = "#2d0e0e";
    statusBar.style.borderColor = "#e60012";
    statusText.style.color = "#ff8585";
  } else {
    statusBar.style.backgroundColor = "#111116";
    statusBar.style.borderColor = "#000000";
    statusText.style.color = "#ffffff";
  }
  statusText.innerText = msg;
  statusIcon.innerText = icon;
}

function updateStatsAndRadar() {
  const orig = boxOrig.value;
  const target = boxTarget.value;

  // Stats for original text
  const charCount = orig.length;
  const words = orig.trim() ? orig.trim().split(/\s+/).length : 0;
  statsOrig.innerText = `${charCount.toLocaleString()} chars | ${words.toLocaleString()} words`;

  // Live Occurrence Radar (handles direct match and CRLF/LF normalized matching)
  if (!target) {
    radarBadge.className = "radar-badge radar-waiting";
    radarBadge.style.backgroundColor = "#222222";
    radarBadge.style.color = "#888888";
    radarBadge.style.borderColor = "#000000";
    radarBadge.innerText = "RADAR: WAITING";
  } else {
    let count = 0;
    if (orig) {
      count = orig.split(target).length - 1;
      if (count === 0 && (orig.includes("\r") || target.includes("\r"))) {
        const normOrig = orig.replace(/\r\n/g, "\n");
        const normTarget = target.replace(/\r\n/g, "\n");
        count = normOrig.split(normTarget).length - 1;
      }
    }
    if (count > 0) {
      radarBadge.className = "radar-badge radar-found";
      radarBadge.style.backgroundColor = "#ffe600";
      radarBadge.style.color = "#000000";
      radarBadge.style.borderColor = "#000000";
      radarBadge.innerText = `🎯 LOCKED: ${count} MATCH${count > 1 ? 'ES' : ''}!`;
    } else {
      radarBadge.className = "radar-badge radar-zero";
      radarBadge.style.backgroundColor = "#3a1111";
      radarBadge.style.color = "#ff9999";
      radarBadge.style.borderColor = "#e60012";
      radarBadge.innerText = "⚠️ 0 MATCHES IN ORIGINAL";
    }
  }
}

boxOrig.addEventListener("input", updateStatsAndRadar);
boxTarget.addEventListener("input", updateStatsAndRadar);

function clearOriginal() {
  playClick();
  boxOrig.value = "";
  updateStatsAndRadar();
  boxOrig.focus();
}

function clearTarget() {
  playClick();
  boxTarget.value = "";
  updateStatsAndRadar();
  boxTarget.focus();
}

function clearResult() {
  playClick();
  boxResult.value = "";
  statsResult.innerText = "0 chars";
  setStatus("Result cleared.", "idle", "💬");
}

async function pasteOriginal() {
  playClick();
  try {
    let text = "";
    if (window.pywebview && window.pywebview.api) {
      text = await window.pywebview.api.read_clipboard();
    }
    if (!text && navigator.clipboard) {
      text = await navigator.clipboard.readText();
    }
    if (text) {
      boxOrig.value = text;
      updateStatsAndRadar();
      setStatus("📋 Pasted original text from clipboard.", "idle", "📋");
    }
  } catch(e) {
    boxOrig.focus();
  }
}

async function pasteTarget() {
  playClick();
  try {
    let text = "";
    if (window.pywebview && window.pywebview.api) {
      text = await window.pywebview.api.read_clipboard();
    }
    if (!text && navigator.clipboard) {
      text = await navigator.clipboard.readText();
    }
    if (text) {
      boxTarget.value = text;
      updateStatsAndRadar();
      setStatus("📋 Pasted target text from clipboard.", "idle", "📋");
    }
  } catch(e) {
    boxTarget.focus();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Execution: All-Out Attack Finisher Trigger
// ─────────────────────────────────────────────────────────────────────────────
async function triggerPurge() {
  const orig = boxOrig.value;
  const target = boxTarget.value;

  if (!orig) {
    playErrorBuzz();
    setStatus("⚠️ Please paste your original text in Box ①.", "error", "⚠️");
    boxOrig.focus();
    return;
  }
  if (!target) {
    playErrorBuzz();
    setStatus("⚠️ Please paste the text to delete in Box ②.", "error", "⚠️");
    boxTarget.focus();
    return;
  }

  let result;
  if (window.pywebview && window.pywebview.api) {
    try {
      const raw = await window.pywebview.api.execute_purge(orig, target);
      result = JSON.parse(raw);
    } catch(e) {
      result = null;
    }
  }

  if (!result) {
    // Pure JS fallback with newline normalization
    let normOrig = orig;
    let normTarget = target;
    let count = orig.split(target).length - 1;

    if (count === 0 && (orig.includes("\r") || target.includes("\r"))) {
      normOrig = orig.replace(/\r\n/g, "\n");
      normTarget = target.replace(/\r\n/g, "\n");
      count = normOrig.split(normTarget).length - 1;
    }

    if (count === 0) {
      result = {
        success: false,
        error: "not_found",
        message: "❌ Target phrase not found! Ensure character-for-character match."
      };
    } else {
      let cleaned = normOrig.split(normTarget).join("");
      cleaned = cleaned.replace(/(?:\r\n){3,}/g, "\r\n\r\n").replace(/\n{3,}/g, "\n\n");
      if (orig.includes("\r\n") && !cleaned.includes("\r")) {
        cleaned = cleaned.replace(/\n/g, "\r\n");
      }
      const removed = orig.length - cleaned.length;
      result = {
        success: true,
        cleaned: cleaned,
        count: count,
        removed_chars: removed,
        message: `★ MISSION ACCOMPLISHED! Eradicated ${count} occurrence(s) (${removed.toLocaleString()} chars removed)!`
      };
    }
  }

  if (!result.success) {
    playErrorBuzz();
    setStatus(result.message, "error", "❌");
    return;
  }

  // Success: populate result (exact content without stripping)
  boxResult.value = result.cleaned;
  statsResult.innerText = `${result.cleaned.length.toLocaleString()} chars (-${result.removed_chars.toLocaleString()} chars)`;
  setStatus(result.message, "success", "✅");

  // All-Out Attack Sound and Slash Animation
  playSlashImpact();

  appContainer.classList.remove("shake-effect");
  void appContainer.offsetWidth; // Trigger reflow
  appContainer.classList.add("shake-effect");

  finisherOverlay.classList.add("active");
  setTimeout(() => {
    finisherOverlay.classList.remove("active");
    appContainer.classList.remove("shake-effect");
  }, 950);
}

// ─────────────────────────────────────────────────────────────────────────────
// Copy Result to Clipboard (Preserves exact whitespace & formatting)
// ─────────────────────────────────────────────────────────────────────────────
async function copyResult() {
  const text = boxResult.value;
  if (!text) {
    playErrorBuzz();
    setStatus("⚠️ Nothing to copy yet - execute removal first!", "error", "⚠️");
    return;
  }

  let copied = false;
  if (window.pywebview && window.pywebview.api) {
    try {
      copied = await window.pywebview.api.copy_clipboard(text);
    } catch(e) {}
  }
  if (!copied && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      copied = true;
    } catch(e) {}
  }

  playVictoryChime();
  setStatus("📋 COPIED TO CLIPBOARD! Target text stolen successfully!", "success", "★");

  btnCopy.classList.add("btn-copy-copied");
  btnCopy.style.backgroundColor = "#00e676";
  btnCopy.style.color = "#000000";
  btnCopyLabel.innerText = "★ RESULT STOLEN TO CLIPBOARD! ★";
  setTimeout(() => {
    btnCopy.classList.remove("btn-copy-copied");
    btnCopy.style.backgroundColor = "#ffe600";
    btnCopy.style.color = "#000000";
    btnCopyLabel.innerText = "📋 COPY RESULT TO CLIPBOARD [CTRL+SHIFT+C]";
  }, 1200);
}

// ─────────────────────────────────────────────────────────────────────────────
// Keyboard Shortcuts & Sound Attachments
// ─────────────────────────────────────────────────────────────────────────────
window.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") {
    e.preventDefault();
    triggerPurge();
  } else if (e.ctrlKey && e.shiftKey && (e.key === "C" || e.key === "c")) {
    e.preventDefault();
    copyResult();
  } else if (e.key === "Escape") {
    finisherOverlay.classList.remove("active");
    appContainer.classList.remove("shake-effect");
  }
});

// Attach hover sound to interactive elements
document.querySelectorAll("button, .ransom-badge").forEach(el => {
  el.addEventListener("mouseenter", playHover);
});

// Initialize stats and SFX status
updateStatsAndRadar();
updateSFXUI();
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────────
# Python-Webview Bridge API Class
# ──────────────────────────────────────────────────────────────────────────────
class Persona5Bridge:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def execute_purge(self, original: str, target: str) -> str:
        """Called asynchronously from JS to perform the purge."""
        res = purge_text_logic(original, target)
        return json.dumps(res)

    def copy_clipboard(self, text: str) -> bool:
        """Copies to the Windows clipboard via safe ctypes."""
        return set_windows_clipboard(text)

    def read_clipboard(self) -> str:
        """Reads from the Windows clipboard via safe ctypes."""
        return get_windows_clipboard()


# ──────────────────────────────────────────────────────────────────────────────
# Tkinter Fallback Engine (High-Contrast Persona 5 with Full Feature Parity)
# ──────────────────────────────────────────────────────────────────────────────
def run_tkinter_p5():
    """Runs a customized high-contrast Persona 5 themed GUI in Tkinter."""
    import tkinter as tk
    from tkinter import scrolledtext

    P5_RED = "#e60012"
    P5_RED_BRIGHT = "#ff1a2d"
    P5_BLACK = "#0a0a0c"
    P5_CARD = "#141418"
    P5_INPUT = "#18181e"
    P5_WHITE = "#ffffff"
    P5_YELLOW = "#ffe600"
    P5_MUTED = "#888892"
    P5_GREEN = "#00e676"

    root = tk.Tk()
    root.title("PERSONA 5 // TEXT PURGE [FALLBACK]")
    root.configure(bg=P5_BLACK)
    root.geometry("820x860")
    root.minsize(680, 720)

    # Load Persona 5 window icon if available
    icon_cands = []
    if hasattr(sys, "_MEIPASS"):
        icon_cands.append(os.path.join(sys._MEIPASS, "p5_icon.ico"))
    if "__file__" in globals():
        icon_cands.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "p5_icon.ico"))
    icon_cands.extend([
        os.path.join(os.path.dirname(sys.executable), "p5_icon.ico"),
        os.path.join(os.getcwd(), "p5_icon.ico"),
        os.path.join(os.path.expanduser("~"), "Desktop", "p5_icon.ico"),
    ])
    for cand in icon_cands:
        if cand and os.path.isfile(cand):
            try:
                root.iconbitmap(cand)
                break
            except Exception:
                pass

    # Calling card banner
    header = tk.Frame(root, bg=P5_RED, padx=14, pady=10)
    header.pack(fill="x", padx=16, pady=(12, 6))
    tk.Label(
        header, text="★ TAKE YOUR TEXT // PHANTOM PURGE PROTOCOL ★",
        font=("Impact", 16), bg=P5_RED, fg=P5_WHITE
    ).pack(side="left")

    def play_sound(sound_type="click"):
        if sys.platform == "win32":
            try:
                import winsound
                if sound_type == "click":
                    winsound.Beep(800, 30)
                elif sound_type == "slash":
                    winsound.Beep(240, 150)
                elif sound_type == "chime":
                    winsound.Beep(1200, 100)
                elif sound_type == "error":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass

    # Header generator helper
    def make_panel_header(parent, title_text, bg_tag, fg_tag, stats_text=""):
        f = tk.Frame(parent, bg=P5_BLACK)
        f.pack(fill="x", pady=(8, 2))
        lbl_tag = tk.Label(
            f, text=title_text, font=("Impact", 12),
            bg=bg_tag, fg=fg_tag, padx=8, pady=2
        )
        lbl_tag.pack(side="left")
        lbl_stats = tk.Label(
            f, text=stats_text, font=("Consolas", 9),
            bg="#000", fg=P5_MUTED, padx=6, pady=2
        )
        lbl_stats.pack(side="right")
        return lbl_stats

    # Panel 1: Original
    stats_orig_label = make_panel_header(root, "★ ① ORIGINAL TEXT", P5_WHITE, "#000", "0 chars | 0 words")
    box_orig = scrolledtext.ScrolledText(
        root, height=8, font=("Consolas", 10),
        bg=P5_INPUT, fg=P5_WHITE, insertbackground=P5_WHITE,
        relief="flat", bd=0, padx=8, pady=8, wrap="word"
    )
    box_orig.pack(fill="both", expand=True, padx=16, pady=(0, 2))

    # Panel 1 buttons
    tools_1 = tk.Frame(root, bg=P5_BLACK)
    tools_1.pack(fill="x", padx=16, pady=(0, 4))
    def paste_to_orig():
        play_sound("click")
        txt = get_windows_clipboard()
        if txt:
            box_orig.delete("1.0", tk.END)
            box_orig.insert("1.0", txt)
            update_radar()
    def clear_orig():
        play_sound("click")
        box_orig.delete("1.0", tk.END)
        update_radar()
    tk.Button(tools_1, text="PASTE [📋]", font=("Impact", 9), bg="#000", fg="#fff",
              command=paste_to_orig, padx=6, pady=2, relief="flat", cursor="hand2").pack(side="right", padx=2)
    tk.Button(tools_1, text="CLEAR [×]", font=("Impact", 9), bg="#000", fg="#fff",
              command=clear_orig, padx=6, pady=2, relief="flat", cursor="hand2").pack(side="right", padx=2)

    # Panel 2: Target
    radar_label = make_panel_header(root, "★ ② TEXT TO DELETE", P5_RED, P5_WHITE, "RADAR: WAITING")
    radar_label.config(fg=P5_YELLOW, font=("Impact", 10))
    box_target = scrolledtext.ScrolledText(
        root, height=4, font=("Consolas", 10),
        bg=P5_INPUT, fg=P5_WHITE, insertbackground=P5_WHITE,
        relief="flat", bd=0, padx=8, pady=8, wrap="word"
    )
    box_target.pack(fill="both", expand=True, padx=16, pady=(0, 2))

    # Panel 2 buttons
    tools_2 = tk.Frame(root, bg=P5_BLACK)
    tools_2.pack(fill="x", padx=16, pady=(0, 4))
    def paste_to_target():
        play_sound("click")
        txt = get_windows_clipboard()
        if txt:
            box_target.delete("1.0", tk.END)
            box_target.insert("1.0", txt)
            update_radar()
    def clear_target():
        play_sound("click")
        box_target.delete("1.0", tk.END)
        update_radar()
    tk.Button(tools_2, text="PASTE [📋]", font=("Impact", 9), bg="#000", fg="#fff",
              command=paste_to_target, padx=6, pady=2, relief="flat", cursor="hand2").pack(side="right", padx=2)
    tk.Button(tools_2, text="CLEAR [×]", font=("Impact", 9), bg="#000", fg="#fff",
              command=clear_target, padx=6, pady=2, relief="flat", cursor="hand2").pack(side="right", padx=2)

    # Live Radar update function
    def update_radar(event=None):
        orig = box_orig.get("1.0", tk.END)
        if orig.endswith("\n"): orig = orig[:-1]
        target = box_target.get("1.0", tk.END)
        if target.endswith("\n"): target = target[:-1]

        char_cnt = len(orig)
        words = len(orig.split()) if orig.strip() else 0
        stats_orig_label.config(text=f"{char_cnt:,} chars | {words:,} words")

        if not target:
            radar_label.config(text="RADAR: WAITING", fg=P5_MUTED)
        else:
            cnt = orig.count(target)
            if cnt == 0 and ("\r" in orig or "\r" in target):
                cnt = orig.replace("\r\n", "\n").count(target.replace("\r\n", "\n"))
            if cnt > 0:
                radar_label.config(text=f"🎯 LOCKED: {cnt} MATCH{'ES' if cnt > 1 else ''}!", fg=P5_YELLOW)
            else:
                radar_label.config(text="⚠️ 0 MATCHES IN ORIGINAL", fg="#ff8585")

    box_orig.bind("<KeyRelease>", update_radar)
    box_target.bind("<KeyRelease>", update_radar)

    # Action bar
    status_var = tk.StringVar(value="💬 READY FOR INFILTRATION - AWAITING COMMAND")
    status_frame = tk.Frame(root, bg=P5_BLACK)
    status_frame.pack(fill="x", padx=16, pady=6)

    def do_purge(event=None):
        orig = box_orig.get("1.0", tk.END)
        if orig.endswith("\n"): orig = orig[:-1]
        target = box_target.get("1.0", tk.END)
        if target.endswith("\n"): target = target[:-1]

        res = purge_text_logic(orig, target)
        if not res["success"]:
            play_sound("error")
            status_var.set(res["message"])
            status_label.config(fg=P5_RED)
            return

        play_sound("slash")
        box_result.config(state="normal")
        box_result.delete("1.0", tk.END)
        box_result.insert("1.0", res["cleaned"])
        box_result.config(state="disabled")

        stats_res_label.config(text=f"{len(res['cleaned']):,} chars (-{res['removed_chars']:,} chars)")
        status_var.set(res["message"])
        status_label.config(fg=P5_GREEN)

    btn_exec = tk.Button(
        status_frame, text="★ EXECUTE PURGE [CTRL+ENTER] ★", command=do_purge,
        font=("Impact", 13), bg=P5_RED, fg=P5_WHITE,
        relief="flat", padx=18, pady=6, cursor="hand2", activebackground=P5_RED_BRIGHT
    )
    btn_exec.pack(side="left")

    status_label = tk.Label(
        status_frame, textvariable=status_var,
        font=("Segoe UI", 10, "bold"), bg=P5_BLACK, fg=P5_MUTED
    )
    status_label.pack(side="left", padx=12)

    # Panel 3: Result
    stats_res_label = make_panel_header(root, "★ ③ CLEANSED RESULT", P5_YELLOW, "#000", "0 chars")
    box_result = scrolledtext.ScrolledText(
        root, height=8, font=("Consolas", 10),
        bg="#0d1810", fg="#bdfccb", insertbackground=P5_WHITE,
        relief="flat", bd=0, padx=8, pady=8, wrap="word", state="disabled"
    )
    box_result.pack(fill="both", expand=True, padx=16, pady=(0, 4))

    def copy_res(event=None):
        box_result.config(state="normal")
        res = box_result.get("1.0", tk.END)
        if res.endswith("\n"): res = res[:-1]
        box_result.config(state="disabled")

        if res:
            set_windows_clipboard(res)
            play_sound("chime")
            status_var.set("★ COPIED TO CLIPBOARD! Target text stolen successfully!")
            status_label.config(fg=P5_GREEN)
            btn_copy.config(bg=P5_GREEN, text="★ RESULT STOLEN TO CLIPBOARD! ★")
            root.after(1200, lambda: btn_copy.config(bg=P5_YELLOW, text="📋 COPY RESULT TO CLIPBOARD [CTRL+SHIFT+C]"))
        else:
            play_sound("error")
            status_var.set("⚠️ Nothing to copy yet - execute removal first.")
            status_label.config(fg=P5_RED)

    btn_copy = tk.Button(
        root, text="📋 COPY RESULT TO CLIPBOARD [CTRL+SHIFT+C]", command=copy_res,
        font=("Impact", 12), bg=P5_YELLOW, fg="#000",
        relief="flat", padx=16, pady=8, cursor="hand2", activebackground=P5_WHITE
    )
    btn_copy.pack(fill="x", padx=16, pady=(6, 14))

    # Bind shortcuts
    root.bind("<Control-Return>", do_purge)
    root.bind("<Control-Shift-C>", copy_res)
    root.bind("<Control-Shift-c>", copy_res)

    root.mainloop()


# ──────────────────────────────────────────────────────────────────────────────
# Edge WebView2 Runtime Auto-Detection & Environment Setup
# ──────────────────────────────────────────────────────────────────────────────
def find_webview2_runtime():
    """
    Locates the Microsoft Edge WebView2 runtime executable directory across
    common install paths, EdgeCore, Edge application directories, and registry keys.
    Returns the folder path containing msedgewebview2.exe or msedge.exe, or None.
    """
    import glob
    import winreg

    def is_valid_runtime_dir(p):
        if not p or not os.path.isdir(p):
            return False
        return (
            os.path.isfile(os.path.join(p, "msedgewebview2.exe"))
            or os.path.isfile(os.path.join(p, "msedge.exe"))
        )

    # 1. Environment variables (only if valid)
    for env_key in ("WEBVIEW2_RUNTIME_PATH", "WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"):
        val = os.environ.get(env_key)
        if is_valid_runtime_dir(val):
            return val

    # 2. Known standard install locations on Windows
    roots = [
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("LOCALAPPDATA", ""),
        os.environ.get("ProgramData", r"C:\ProgramData"),
    ]
    subdirs = [
        r"Microsoft\EdgeCore",
        r"Microsoft\EdgeWebView\Application",
        r"Microsoft\Edge\Application",
        r"Microsoft\EdgeUpdate\Install",
    ]

    for root in roots:
        if not root:
            continue
        for sub in subdirs:
            base = os.path.join(root, sub)
            if not os.path.isdir(base):
                continue
            # Check root of subdir directly
            if is_valid_runtime_dir(base):
                return base
            # Check version subdirectories (e.g. EdgeCore\152.0.4191.53)
            try:
                for vdir in sorted(glob.glob(os.path.join(base, "*")), reverse=True):
                    if is_valid_runtime_dir(vdir):
                        return vdir
                    # Check 2 levels deep for EdgeUpdate\Install\{GUID}\version
                    for sub2 in sorted(glob.glob(os.path.join(vdir, "*")), reverse=True):
                        if is_valid_runtime_dir(sub2):
                            return sub2
            except Exception:
                pass

    # 3. Registry checks
    for hkey in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for reg_path in (
            r"SOFTWARE\Microsoft\EdgeUpdate\ClientState\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\ClientState\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
        ):
            try:
                with winreg.OpenKey(hkey, reg_path) as k:
                    for val_name in ("location", "Path", ""):
                        try:
                            val, _ = winreg.QueryValueEx(k, val_name)
                            if val:
                                if is_valid_runtime_dir(val):
                                    return val
                                dirname = os.path.dirname(val)
                                if is_valid_runtime_dir(dirname):
                                    return dirname
                        except Exception:
                            pass
            except Exception:
                pass

    return None


def setup_webview2_environment():
    """Configures Edge Chromium WebView2 runtime and disables forced color stripping."""
    if sys.platform != "win32":
        return

    runtime_dir = find_webview2_runtime()
    if runtime_dir:
        os.environ["WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"] = runtime_dir

    # Pass Chromium flags to disable forced colors, contrast themes, and enforce dark mode
    existing_args = os.environ.get("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "")
    flags_to_add = [
        "--disable-features=ForcedColors,ContrastThemes",
        "--enable-features=DarkLightMode",
        "--force-dark-mode",
        "--high-contrast-mode=0",
    ]
    new_flags = [f for f in flags_to_add if f not in existing_args]
    if new_flags:
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
            existing_args + " " + " ".join(new_flags)
        ).strip()


# ──────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────────────────────────
def main():
    """Launches the Persona 5 desktop application."""
    setup_webview2_environment()

    icon_path = None
    script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
    icon_cands = []
    if hasattr(sys, "_MEIPASS"):
        icon_cands.append(os.path.join(sys._MEIPASS, "p5_icon.ico"))
    if script_dir:
        icon_cands.append(os.path.join(script_dir, "p5_icon.ico"))
    icon_cands.extend([
        os.path.join(os.path.dirname(sys.executable), "p5_icon.ico"),
        os.path.join(os.getcwd(), "p5_icon.ico"),
        os.path.join(os.path.expanduser("~"), "Desktop", "p5_icon.ico"),
    ])
    for cand in icon_cands:
        if cand and os.path.isfile(cand):
            icon_path = cand
            break

    # Attempt pywebview first for maximum visual fidelity & Web Audio
    try:
        import webview

        runtime_dir = find_webview2_runtime()
        if runtime_dir:
            webview.settings["WEBVIEW2_RUNTIME_PATH"] = runtime_dir

        bridge = Persona5Bridge()
        window = webview.create_window(
            title="PERSONA 5 // THE PHANTOM TEXT PURGE",
            html=PERSONA_5_HTML,
            js_api=bridge,
            width=860,
            height=920,
            min_size=(680, 720),
            resizable=True,
            background_color="#0a0a0c"
        )
        bridge.set_window(window)

        if icon_path:
            webview.start(gui="edgechromium", icon=icon_path)
        else:
            webview.start(gui="edgechromium")
    except Exception as e:
        # Fallback gracefully to Tkinter P5 UI if pywebview or WebView2 fails
        print(f"[Persona 5] Webview initialization note: {e}. Launching fallback GUI...")
        run_tkinter_p5()


if __name__ == "__main__":
    main()
