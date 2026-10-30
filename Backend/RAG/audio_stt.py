
from google.genai import types

from Backend.LLM.model import get_llm, MODEL_NAME


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str
) -> str:
    """Convert recorded audio into text using Gemini."""

    if not audio_bytes:
        raise ValueError("The recorded audio is empty.")

    allowed_types = {
        "audio/webm",
        "audio/wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/ogg",
    }

    if mime_type not in allowed_types:
        raise ValueError(
            f"Unsupported audio format: {mime_type}"
        )

    client = get_llm()

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type
    )

    prompt = """
    Transcribe the user's recorded speech accurately.

    Instructions:
    - Return only the spoken words.
    - Do not answer the spoken question.
    - Do not summarize or add explanations.
    - Preserve the language spoken by the user.
    - Do not invent words that are not audible.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, audio_part]
    )

    transcript = response.text

    if not transcript or not transcript.strip():
        raise ValueError("No speech could be recognized.")

    return transcript.strip()
