
import pdfplumber
import pandas as pd


def extract_tables_from_pdf(file_path: str) -> pd.DataFrame:
    """
    Extract tables from a text-based PDF
    and return them as a single DataFrame.
    """

    extracted_tables = []

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:

                if not table or len(table) < 2:
                    continue

                headers = table[0]
                rows = table[1:]

                df = pd.DataFrame(
                    rows,
                    columns=headers
                )

                extracted_tables.append(df)

    if not extracted_tables:
        raise ValueError(
            "No readable tables found in this PDF."
        )

    final_df = pd.concat(
        extracted_tables,
        ignore_index=True
    )

    return final_df
