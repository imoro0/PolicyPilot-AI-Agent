
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from Backend.Services.chat_service import chat_with_audio
from pydantic import BaseModel
import os
import tempfile
from Backend.Services.chat_service import answer_tabular_question
from Backend.Services.chat_service import analyze_uploaded_file

from Backend.Schemas.chat import ChatRequest, ChatResponse
from Backend.Services.chat_service import (
    chat_with_policy_agent,
    chat_with_image,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = chat_with_policy_agent(
        question=request.question,
        session_id=request.session_id
    )

    return ChatResponse(answer=answer)


@router.post("/chat/image", response_model=ChatResponse)
async def chat_with_image_endpoint(
    image: UploadFile = File(...),
    question: str = Form(
        default="Please explain the text in this image."
    ),
    session_id: str = Form(default="default"),
):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG, PNG, WEBP, or GIF image."
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty."
        )

    try:
        answer = await chat_with_image(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            question=question,
            session_id=session_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Image processing failed. Please try again."
        ) from error
    finally:
        await image.close()

    return ChatResponse(answer=answer)


class AudioChatResponse(BaseModel):
    transcript: str
    answer: str


@router.post("/chat/audio", response_model=AudioChatResponse)
async def chat_with_audio_endpoint(
    audio: UploadFile = File(...),
    session_id: str = Form(default="default"),
):
    allowed_types = {
        "audio/webm",
        "audio/wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/ogg",
    }

    mime_type = (audio.content_type or "").split(";")[0].strip().lower()

    if mime_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format. Please record audio again."
        )

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="The recorded audio is empty."
        )

    if len(audio_bytes) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio must be smaller than 20 MB."
        )

    try:
        result = chat_with_audio(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            session_id=session_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Audio processing failed. Please try again."
        ) from error
    finally:
        await audio.close()

    return AudioChatResponse(**result)



@router.post("/chat/file")
async def chat_with_file_endpoint(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    allowed_types = {
        ".csv",
        ".xlsx",
        ".xls",
        ".pdf"
    }

    filename = file.filename or ""
    extension = os.path.splitext(filename)[1].lower()

    if extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV, Excel, or PDF file."
        )

    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question about the uploaded file."
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File must be smaller than 20 MB."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        answer = answer_tabular_question(
            file_path=temp_path,
            question=question
        )

        return {
            "filename": filename,
            "question": question,
            "answer": answer
        }

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="File processing failed. Please try again."
        ) from error

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()
