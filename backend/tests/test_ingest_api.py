"""
Unit tests for the Ingestion API.
"""

from __future__ import annotations

import pytest

from app.core.file_detection import detect_input_type, detect_mime_from_bytes
from app.models.enums import InputType


class TestFileDetection:
    """Tests for the magic-bytes file type detection."""

    def test_detect_png(self):
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        assert detect_input_type(data=png_header) == InputType.IMAGE

    def test_detect_jpeg(self):
        jpeg_header = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        assert detect_input_type(data=jpeg_header) == InputType.IMAGE

    def test_detect_pdf(self):
        pdf_header = b"%PDF-1.4" + b"\x00" * 100
        assert detect_input_type(data=pdf_header) == InputType.PDF

    def test_detect_mp3(self):
        mp3_header = b"ID3" + b"\x00" * 100
        assert detect_input_type(data=mp3_header) == InputType.AUDIO

    def test_detect_from_filename(self):
        assert detect_input_type(filename="test.mp4") == InputType.VIDEO
        assert detect_input_type(filename="test.wav") == InputType.AUDIO
        assert detect_input_type(filename="test.eml") == InputType.EMAIL

    def test_detect_from_content_type(self):
        assert detect_input_type(content_type="video/mp4") == InputType.VIDEO
        assert detect_input_type(content_type="image/jpeg") == InputType.IMAGE

    def test_unknown_returns_none(self):
        assert detect_input_type(data=b"\x00\x01\x02\x03") is None
        assert detect_input_type(filename="test.xyz") is None

    def test_mime_detection_wav(self):
        wav_header = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"\x00" * 100
        mime = detect_mime_from_bytes(wav_header)
        assert mime == "audio/wav"
