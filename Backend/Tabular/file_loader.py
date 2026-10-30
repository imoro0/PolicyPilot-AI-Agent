
import os
import pandas as pd

from Backend.Tabular.pdf_table_extractor import (
    extract_tables_from_pdf
)


def load_tabular_file(file_path: str) -> pd.DataFrame:
    """
    Load CSV, Excel, or PDF files
    and return a pandas DataFrame.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    elif extension == ".pdf":
        df = extract_tables_from_pdf(file_path)

    else:
        raise ValueError(
            "Unsupported file format. "
            "Please upload CSV, Excel, or PDF."
        )

    if df.empty:
        raise ValueError(
            "The uploaded file contains no data."
        )

    return df
