"""Offline text-to-speech engine for VaultMind.

Supports multiple TTS backends based on available hardware:
- Piper TTS: Lightweight, CPU-only, runs on Raspberry Pi (~15-65MB models)
- Chatterbox TTS: High-quality, GPU required (~4.5-8GB VRAM)
- Kokoro TTS: Mid-range, CPU-friendly (82M params)

All backends run fully offline after initial model download.
"""

from __future__ import annotations

import io
import logging
import subprocess
import wave
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_VOICE_DIR = "data/voices"


class TTSBackend(Enum):
    PIPER = "piper"
    CHATTERBOX = "chatterbox"
    KOKORO = "kokoro"
    ESPEAK = "espeak"


def detect_available_backend() -> TTSBackend:
    """Auto-detect the best available TTS backend."""
    # Try Piper first (best for edge devices)
    try:
        import piper  # noqa: F401
        return TTSBackend.PIPER
    except ImportError:
        pass

    # Try Chatterbox (best quality, needs GPU)
    try:
        import chatterbox  # noqa: F401
        return TTSBackend.CHATTERBOX
    except ImportError:
        pass

    # Try Kokoro (good CPU fallback)
    try:
        import kokoro  # noqa: F401
        return TTSBackend.KOKORO
    except ImportError:
        pass

    # Fallback to espeak-ng (always available on Linux)
    return TTSBackend.ESPEAK


def synthesize(
    text: str,
    output_path: str | Path | None = None,
    backend: TTSBackend | None = None,
    voice: str | None = None,
) -> bytes:
    """Synthesize text to speech and return WAV bytes.

    Args:
        text: Text to synthesize.
        output_path: Optional path to save the WAV file.
        backend: TTS backend to use. Auto-detected if None.
        voice: Voice/model name (backend-specific).

    Returns:
        WAV audio data as bytes.
    """
    if backend is None:
        backend = detect_available_backend()

    logger.info("TTS backend: %s", backend.value)

    if backend == TTSBackend.PIPER:
        audio = _synthesize_piper(text, voice)
    elif backend == TTSBackend.CHATTERBOX:
        audio = _synthesize_chatterbox(text, voice)
    elif backend == TTSBackend.KOKORO:
        audio = _synthesize_kokoro(text, voice)
    else:
        audio = _synthesize_espeak(text, voice)

    if output_path:
        Path(output_path).write_bytes(audio)
        logger.info("Audio saved to %s", output_path)

    return audio


def _synthesize_piper(text: str, voice: str | None = None) -> bytes:
    """Synthesize using Piper TTS (CPU, lightweight, edge-friendly).

    Piper models are ONNX-based, ~15-65MB each.
    Download voices from: https://github.com/rhasspy/piper/blob/master/VOICES.md
    """
    from piper import PiperVoice

    voice_path = voice or _find_piper_voice()
    if not voice_path:
        raise FileNotFoundError(
            "No Piper voice model found. Download a .onnx voice to data/voices/"
        )

    piper_voice = PiperVoice.load(voice_path)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        piper_voice.synthesize(text, wav_file)
    return buffer.getvalue()


def _synthesize_chatterbox(text: str, voice: str | None = None) -> bytes:
    """Synthesize using Chatterbox TTS (GPU, high quality, voice cloning).

    Requires ~4.5GB VRAM (Turbo) or ~8GB VRAM (Original).
    Runs offline after initial model download (~1GB).
    """
    import torch
    import torchaudio

    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        model = ChatterboxTurboTTS.from_pretrained(device=device)
    except ImportError:
        from chatterbox.tts import ChatterboxTTS
        model = ChatterboxTTS.from_pretrained(device=device)

    wav = model.generate(text, audio_prompt_path=voice)
    buffer = io.BytesIO()
    torchaudio.save(buffer, wav, model.sr, format="wav")
    return buffer.getvalue()


def _synthesize_kokoro(text: str, voice: str | None = None) -> bytes:
    """Synthesize using Kokoro TTS (CPU-friendly, 82M params).

    Supports 9 languages, 26 voices. Apache 2.0 license.
    """
    import soundfile as sf
    from kokoro import KPipeline

    pipeline = KPipeline(lang_code="a")  # American English
    voice_name = voice or "af_heart"
    generator = pipeline(text, voice=voice_name)

    audio_chunks = []
    for _gs, _ps, audio in generator:
        audio_chunks.append(audio)

    import numpy as np
    full_audio = np.concatenate(audio_chunks)

    buffer = io.BytesIO()
    sf.write(buffer, full_audio, 24000, format="WAV")
    return buffer.getvalue()


def _synthesize_espeak(text: str, voice: str | None = None) -> bytes:
    """Synthesize using espeak-ng (last resort, robotic but universal)."""
    voice_arg = voice or "en"
    result = subprocess.run(
        ["espeak-ng", "-v", voice_arg, "--stdout", text],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"espeak-ng failed: {result.stderr.decode()}")
    return result.stdout


def _find_piper_voice() -> str | None:
    """Find the first available Piper .onnx voice model."""
    voice_dir = Path(DEFAULT_VOICE_DIR)
    if voice_dir.is_dir():
        for onnx in voice_dir.glob("*.onnx"):
            return str(onnx)
    return None


def list_backends() -> list[dict]:
    """List available TTS backends and their status."""
    backends = []

    for backend in TTSBackend:
        try:
            if backend == TTSBackend.PIPER:
                import piper  # noqa: F401
                available = True
                note = "CPU, edge-friendly, 15-65MB models"
            elif backend == TTSBackend.CHATTERBOX:
                import chatterbox  # noqa: F401
                available = True
                note = "GPU required, high quality, voice cloning"
            elif backend == TTSBackend.KOKORO:
                import kokoro  # noqa: F401
                available = True
                note = "CPU-friendly, 82M params, 9 languages"
            elif backend == TTSBackend.ESPEAK:
                result = subprocess.run(
                    ["espeak-ng", "--version"],
                    capture_output=True, timeout=3,
                )
                available = result.returncode == 0
                note = "Robotic but universal, 2MB"
            else:
                available = False
                note = "Unknown"
        except (ImportError, FileNotFoundError, subprocess.TimeoutExpired):
            available = False
            note = "Not installed"

        backends.append({
            "name": backend.value,
            "available": available,
            "note": note,
        })

    return backends
