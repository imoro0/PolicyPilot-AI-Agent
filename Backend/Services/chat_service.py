
from Backend.Agent.graph import run_agent
from Backend.RAG.image_ocr import extract_text_from_image
from Backend.Tabular.file_loader import load_tabular_file
from Backend.Tabular.data_analyzer import analyze_dataframe
import json

from Backend.LLM.model import get_llm, MODEL_NAME


def chat_with_policy_agent(
    question: str,
    session_id: str = "default"
) -> str:
    """Send a text question to the existing LangGraph agent."""

    question = question.strip()

    if not question:
        return "Please enter a question about Airbnb policies."

    return run_agent(
        question=question,
        session_id=session_id
    )


async def chat_with_image(
    image_bytes: bytes,
    mime_type: str,
    question: str = "Please explain the text in this image.",
    session_id: str = "default",
) -> str:
    """Extract image text with Gemini and send it to the existing agent."""

    extracted_text = extract_text_from_image(
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    question = question.strip()

    if not question:
        question = "Please explain the text in this image."

    combined_question = (
        f"User's question about the uploaded image:\n{question}\n\n"
        f"Text extracted from the image:\n{extracted_text}\n\n"
        "Answer the user's question using the extracted text and "
        "relevant policy information available through the existing "
        "policy agent. Distinguish image text from verified policy facts."
    )

    return run_agent(
        question=combined_question,
        session_id=session_id,
    )


from Backend.RAG.audio_stt import transcribe_audio


def chat_with_audio(
    audio_bytes: bytes,
    mime_type: str,
    session_id: str = "default",
) -> dict:
    """Transcribe recorded audio and send it to PolicyPilot."""

    transcript = transcribe_audio(
        audio_bytes=audio_bytes,
        mime_type=mime_type,
    )

    answer = chat_with_policy_agent(
        question=transcript,
        session_id=session_id,
    )

    return {
        "transcript": transcript,
        "answer": answer,
    }

def analyze_uploaded_file(file_path: str) -> dict:
    """
    Load an uploaded tabular file and generate its summary.
    """

    df = load_tabular_file(file_path)

    analysis = analyze_dataframe(df)

    return {
        "filename": file_path.split("\\")[-1],
        "analysis": analysis
    }


def answer_tabular_question(
    file_path: str,
    question: str
) -> str:
    """
    Answer a user's question using an uploaded tabular dataset.
    """

    question = question.strip()

    if not question:
        return "Please enter a question about the uploaded dataset."

    # Load uploaded file
    df = load_tabular_file(file_path)

    # Generate dataset summary
    summary = analyze_dataframe(df)

    # Prepare dataset content for Gemini
    dataset_content = df.to_csv(index=False)

    if len(dataset_content) > 30000:
        raise ValueError(
            "This dataset is too large for the current "
            "analysis workflow. Please upload a smaller file."
        )

    prompt = f"""
You are PolicyPilot's Tabular Data Analyst.

Answer the user's question using only the provided dataset.

Instructions:
- Understand the dataset columns before answering.
- Use the actual data to support your answer.
- Do not invent values or statistics.
- If the dataset does not contain enough information,
  clearly explain that.
- Keep the answer clear and easy to understand.
- Include calculations or relevant figures when possible.

Dataset Summary:
{json.dumps(summary, indent=2, default=str)}

Dataset:
{dataset_content}

User Question:
{question}
"""

    client = get_llm()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError(
            "Gemini could not generate an answer."
        )

    return response.text.strip()
