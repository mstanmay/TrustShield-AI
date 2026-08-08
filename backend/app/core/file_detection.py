"""
File type detection using magic bytes — not just file extensions.
Maps detected MIME types to InputType enum values.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import BinaryIO

from app.models.enums import InputType

logger = logging.getLogger(__name__)

# Magic byte signatures for common file types
MAGIC_SIGNATURES: list[tuple[bytes, str]] = [
    # Video
    (b"\x00\x00\x00\x18ftypmp4", "video/mp4"),
    (b"\x00\x00\x00\x1cftypisom", "video/mp4"),
    (b"\x00\x00\x00\x20ftypisom", "video/mp4"),
    (b"\x1aE\xdf\xa3", "video/webm"),  # WebM/Matroska
    (b"RIFF", "video/avi"),  # Also could be audio WAV — disambiguate later
    (b"\x00\x00\x00\x1cftypM4V", "video/mp4"),
    # Image
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # Also RIFF — check further bytes
    (b"BM", "image/bmp"),
    # Audio
    (b"ID3", "audio/mpeg"),  # MP3 with ID3 tag
    (b"\xff\xfb", "audio/mpeg"),  # MP3
    (b"\xff\xf3", "audio/mpeg"),  # MP3
    (b"fLaC", "audio/flac"),
    (b"OggS", "audio/ogg"),
    # PDF
    (b"%PDF", "application/pdf"),
    # Email
    (b"From ", "message/rfc822"),
    (b"Return-Path:", "message/rfc822"),
    (b"Received:", "message/rfc822"),
]

# MIME to InputType mapping
MIME_TO_INPUT_TYPE: dict[str, InputType] = {
    "video/mp4": InputType.VIDEO,
    "video/webm": InputType.VIDEO,
    "video/avi": InputType.VIDEO,
    "video/quicktime": InputType.VIDEO,
    "video/x-msvideo": InputType.VIDEO,
    "image/png": InputType.IMAGE,
    "image/jpeg": InputType.IMAGE,
    "image/gif": InputType.IMAGE,
    "image/webp": InputType.IMAGE,
    "image/bmp": InputType.IMAGE,
    "image/tiff": InputType.IMAGE,
    "audio/mpeg": InputType.AUDIO,
    "audio/wav": InputType.AUDIO,
    "audio/flac": InputType.AUDIO,
    "audio/ogg": InputType.AUDIO,
    "audio/mp4": InputType.AUDIO,
    "application/pdf": InputType.PDF,
    "message/rfc822": InputType.EMAIL,
}


def detect_mime_from_bytes(data: bytes) -> str | None:
    """Detect MIME type from file magic bytes."""
    # Try python-magic first (wraps libmagic)
    try:
        import magic
        mime = magic.from_buffer(data[:8192], mime=True)
        if mime:
            return mime
    except (ImportError, Exception):
        pass

    # Fallback: manual signature matching
    for signature, mime_type in MAGIC_SIGNATURES:
        if data[:len(signature)] == signature:
            # Disambiguate RIFF (AVI vs WAV vs WebP)
            if signature == b"RIFF" and len(data) > 11:
                sub = data[8:12]
                if sub == b"WAVE":
                    return "audio/wav"
                elif sub == b"AVI ":
                    return "video/avi"
                elif sub == b"WEBP":
                    return "image/webp"
            return mime_type

    return None


def detect_input_type(
    data: bytes | None = None,
    filename: str | None = None,
    content_type: str | None = None,
) -> InputType | None:
    """Detect InputType from magic bytes, falling back to filename/content-type.

    Priority: magic bytes > content-type header > file extension.
    """
    # 1. Magic bytes (most reliable)
    if data:
        mime = detect_mime_from_bytes(data)
        if mime and mime in MIME_TO_INPUT_TYPE:
            return MIME_TO_INPUT_TYPE[mime]

    # 2. Content-Type header
    if content_type and content_type in MIME_TO_INPUT_TYPE:
        return MIME_TO_INPUT_TYPE[content_type]

    # 3. File extension fallback
    if filename:
        ext = Path(filename).suffix.lower()
        ext_map = {
            ".mp4": InputType.VIDEO, ".avi": InputType.VIDEO, ".mov": InputType.VIDEO,
            ".mkv": InputType.VIDEO, ".webm": InputType.VIDEO,
            ".png": InputType.IMAGE, ".jpg": InputType.IMAGE, ".jpeg": InputType.IMAGE,
            ".gif": InputType.IMAGE, ".bmp": InputType.IMAGE, ".webp": InputType.IMAGE,
            ".tiff": InputType.IMAGE,
            ".mp3": InputType.AUDIO, ".wav": InputType.AUDIO, ".flac": InputType.AUDIO,
            ".ogg": InputType.AUDIO, ".m4a": InputType.AUDIO,
            ".pdf": InputType.PDF,
            ".eml": InputType.EMAIL,
        }
        if ext in ext_map:
            return ext_map[ext]

    return None


def is_likely_qr_code(data: bytes) -> bool:
    """Heuristic check if an image likely contains a QR code.
    Full QR decoding happens in the phishing agent."""
    # This is a pre-filter; actual QR detection is done by pyzbar in the agent
    # For now, any image could contain a QR code
    mime = detect_mime_from_bytes(data)
    return mime is not None and mime.startswith("image/")
