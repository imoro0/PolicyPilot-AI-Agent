# 'from langchain_ollama import ChatOllama


# def get_llm():
#     return ChatOllama(
#         model="qwen3:4b",
#         temperature=0,
#         keep_alive="30m",
#         num_predict=256
#     )


# if __name__ == "__main__":
#     llm = get_llm()

#     response = llm.invoke(
#         "Say hello in one short sentence."
#     )

#     print(response.content)




import os

from google import genai

MODEL_NAME = "models/gemini-3.5-flash-lite"


def get_llm():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in the .env file."
        )

    return genai.Client(api_key=api_key)
