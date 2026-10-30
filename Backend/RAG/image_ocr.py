
from google.genai import types

from Backend.LLM.model import get_llm, MODEL_NAME


def extract_text_from_image(
    image_bytes: bytes,
    mime_type: str
) -> str:
    """
    Extract readable text from a screenshot or document image
    using the existing Gemini API configuration.
    """

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    if mime_type not in allowed_types:
        raise ValueError(
            "Unsupported image format. Use JPG, PNG, WEBP, or GIF."
        )

    client = get_llm()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = """
    Extract the readable text from this screenshot or document image.

    Instructions:
    - Return only the text visible in the image.
    - Preserve the original wording as closely as possible.
    - Keep headings, paragraphs, and lists readable.
    - Do not summarize, answer questions, or invent missing text.
    - If no readable text exists, say: No readable text found.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, image_part]
    )

    extracted_text = response.text

    if not extracted_text or not extracted_text.strip():
        raise ValueError("Gemini could not extract readable text.")

    return extracted_text.strip()
