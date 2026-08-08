"""
Voice Analysis Agent (3b)

Analyzes audio for:
- Synthetic speech artifacts (unnaturally smooth F0 contours, absence of micro-variations)
- Spectral inconsistencies (spectral flatness, harmonic ratios)
- Voice biometric matching against known-speaker reference set
- Audio fingerprinting for reused-scam-audio detection (chromaprint-style hashing)

Uses librosa for spectral analysis.
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from app.agents.base import BaseAgent
from app.core.observability import traced_agent
from app.models.enums import AgentType
from app.models.schemas import Evidence, VoiceResult

logger = logging.getLogger(__name__)


class VoiceAnalysisAgent(BaseAgent):
    """Agent 3b: Voice/audio analysis for synthetic speech and impersonation detection."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.VOICE

    @traced_agent("voice")
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> VoiceResult:
        """Run voice analysis on an audio file."""
        evidence: list[Evidence] = []
        raw_output: dict[str, Any] = {}

        # If input is video, extract audio track first
        audio_path = input_path
        temp_audio = None
        if metadata.get("input_type") in ("video", "VIDEO"):
            audio_path, temp_audio = await self._extract_audio_from_video(input_path)
            if not audio_path:
                return VoiceResult(
                    result="Could not extract audio from video",
                    confidence_score=0.0,
                    evidence=[Evidence(finding="Audio extraction failed", severity="info")],
                    raw_model_output={"error": "audio extraction failed"},
                )

        try:
            import librosa
        except ImportError:
            logger.error("librosa not installed — voice analysis unavailable")
            return VoiceResult(
                result="Voice analysis unavailable — librosa not installed",
                confidence_score=0.0,
                evidence=[Evidence(finding="librosa not installed", severity="warning")],
                raw_model_output={"error": "librosa not installed"},
            )

        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            raw_output["duration_seconds"] = float(duration)
            raw_output["sample_rate"] = int(sr)

            # ── 1. Synthetic Speech Detection ────────────────────────────
            synthetic_score = 0.0

            # F0 (fundamental frequency) analysis
            f0, voiced_flag, _ = librosa.pyin(
                y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
            )
            voiced_f0 = f0[voiced_flag] if voiced_flag is not None else f0[~np.isnan(f0)]

            if len(voiced_f0) > 10:
                f0_std = float(np.std(voiced_f0))
                f0_mean = float(np.mean(voiced_f0))
                raw_output["f0_std"] = f0_std
                raw_output["f0_mean"] = f0_mean

                # Unnaturally smooth F0 = possible TTS
                # Human speech typically has f0_std > 15-20 Hz
                if f0_std < 10:
                    synthetic_score += 0.4
                    evidence.append(Evidence(
                        finding=f"Unnaturally smooth pitch contour (F0 std: {f0_std:.1f} Hz — normal is >15 Hz)",
                        severity="warning",
                        detail={"f0_std": f0_std, "f0_mean": f0_mean},
                    ))
                elif f0_std < 15:
                    synthetic_score += 0.2

                # Check for micro-pauses / breathing artifacts (humans have them, TTS often doesn't)
                silent_frames = np.sum(librosa.amplitude_to_db(np.abs(y)) < -40) / len(y)
                raw_output["silent_ratio"] = float(silent_frames)
                if silent_frames < 0.02 and duration > 5:
                    synthetic_score += 0.2
                    evidence.append(Evidence(
                        finding="Very few natural pauses/breathing detected",
                        severity="info",
                        detail={"silent_ratio": float(silent_frames)},
                    ))

            # ── 2. Spectral Inconsistency Detection ──────────────────────
            spectral_score = 0.0

            # Spectral flatness (white noise vs. tonal)
            spec_flat = librosa.feature.spectral_flatness(y=y)
            mean_flatness = float(np.mean(spec_flat))
            raw_output["spectral_flatness"] = mean_flatness

            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            mean_rolloff = float(np.mean(rolloff))
            raw_output["spectral_rolloff"] = mean_rolloff

            # Harmonic-to-noise ratio
            harmonic, percussive = librosa.effects.hpss(y)
            hnr = float(np.mean(np.abs(harmonic)) / (np.mean(np.abs(percussive)) + 1e-10))
            raw_output["hnr"] = hnr

            # Abnormally high spectral flatness can indicate vocoder artifacts
            if mean_flatness > 0.3:
                spectral_score += 0.3
                evidence.append(Evidence(
                    finding=f"High spectral flatness ({mean_flatness:.3f}) — possible vocoder artifacts",
                    severity="warning",
                    detail={"spectral_flatness": mean_flatness},
                ))

            # Very high or narrow rolloff range
            rolloff_std = float(np.std(rolloff))
            if rolloff_std < 500:
                spectral_score += 0.2
                evidence.append(Evidence(
                    finding=f"Narrow spectral rolloff variation ({rolloff_std:.0f} Hz) — consistent with synthetic audio",
                    severity="info",
                    detail={"rolloff_std": rolloff_std},
                ))

            # ── 3. Audio Fingerprint for Reuse Detection ─────────────────
            audio_fingerprint = self._compute_spectral_fingerprint(y, sr)
            raw_output["audio_fingerprint"] = audio_fingerprint

            # ── 4. Speaker Verification (MFCC similarity placeholder) ────
            # TODO: upgrade to trained model — implement real speaker embedding (e.g., d-vector / x-vector)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            mfcc_mean = np.mean(mfccs, axis=1).tolist()
            raw_output["mfcc_features"] = mfcc_mean

            # Combine scores
            overall_confidence = min(
                synthetic_score * 0.5 + spectral_score * 0.5,
                1.0,
            )

            if overall_confidence > 0.5:
                result_text = "HIGH probability of synthetic/manipulated audio detected"
            elif overall_confidence > 0.25:
                result_text = "MODERATE indicators of possible synthetic audio"
            else:
                result_text = "Audio appears to be natural human speech"

            return VoiceResult(
                result=result_text,
                confidence_score=overall_confidence,
                evidence=evidence,
                raw_model_output=raw_output,
                synthetic_speech_score=synthetic_score,
                spectral_anomaly_score=spectral_score,
                speaker_match_score=None,  # TODO: implement speaker DB lookup
                audio_fingerprint=audio_fingerprint,
                duration_seconds=float(duration),
                sample_rate=int(sr),
            )

        finally:
            # Clean up temp audio if extracted from video
            if temp_audio:
                Path(temp_audio).unlink(missing_ok=True)

    def _compute_spectral_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """Compute a spectral hash fingerprint for audio reuse detection.

        Uses mel-spectrogram → binary hash. Similar to chromaprint but simpler.
        """
        import librosa

        # Compute mel spectrogram
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=32, hop_length=512)
        mel_db = librosa.power_to_db(mel, ref=np.max)

        # Binarize: each mel band above/below its median
        binary = (mel_db > np.median(mel_db, axis=1, keepdims=True)).astype(np.uint8)

        # Hash the binary matrix
        fingerprint = hashlib.sha256(binary.tobytes()).hexdigest()[:32]
        return fingerprint

    async def _extract_audio_from_video(self, video_path: str) -> tuple[str | None, str | None]:
        """Extract audio track from video using ffmpeg."""
        try:
            temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_audio.close()

            result = subprocess.run(
                [
                    "ffmpeg", "-i", video_path,
                    "-vn", "-acodec", "pcm_s16le",
                    "-ar", "16000", "-ac", "1",
                    "-y", temp_audio.name,
                ],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                return temp_audio.name, temp_audio.name
            else:
                logger.error("ffmpeg audio extraction failed: %s", result.stderr.decode())
                Path(temp_audio.name).unlink(missing_ok=True)
                return None, None
        except Exception as e:
            logger.error("Audio extraction error: %s", e)
            return None, None
