
import pandas as pd


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """
    Generate a basic summary of an uploaded tabular dataset.
    """

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    summary = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "column_data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(count)
            for column, count in df.isnull().sum().items()
        },
        "numeric_summary": {}
    }

    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        summary["numeric_summary"] = (
            numeric_df.describe().to_dict()
        )

    return summary
