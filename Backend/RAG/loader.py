
from pathlib import Path
from pypdf import PdfReader

# Project ka root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Policy PDFs ka folder
POLICIES_DIR = PROJECT_ROOT / "Data" / "Policies"


def load_policy_pdfs():
    documents = []

    # Tamam category folders mein PDF files search karo
    for pdf_path in sorted(POLICIES_DIR.rglob("*")):
        if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":
            reader = PdfReader(str(pdf_path))

            # PDF ke tamam pages se text extract karo
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            ).strip()

            # Sirf readable text wali PDFs add karo
            if text:
                documents.append({
                    "text": text,
                    "source": pdf_path.name,
                    "category": pdf_path.parent.name
                })

    return documents
