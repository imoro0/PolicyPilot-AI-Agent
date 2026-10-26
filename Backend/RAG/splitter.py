
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_policy_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = []

    for document in documents:
        text_chunks = splitter.split_text(document["text"])

        for chunk_text in text_chunks:
            chunks.append({
                "text": chunk_text,
                "source": document["source"],
                "category": document["category"]
            })

    return chunks
