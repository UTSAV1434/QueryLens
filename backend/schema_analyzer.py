import pandas as pd
from typing import Dict, Any, List

class SchemaAnalyzer:
    """
    Deep module responsible for extracting and formatting schema information
    from pandas DataFrames. It isolates pandas-specific data profiling logic
    from the HTTP presentation layer and LLM prompt generation.
    """
    
    @staticmethod
    def extract_schema_dict(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """
        Extract a structured dictionary representing the schema,
        suitable for JSON serialization in the HTTP layer.
        """
        columns = []
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].count()),
                "unique_count": int(df[col].nunique()),
            }
            if df[col].dtype == "object":
                col_info["sample_values"] = df[col].unique()[:10].tolist()
            elif df[col].dtype in ["int64", "float64"]:
                col_info["min"] = float(df[col].min())
                col_info["max"] = float(df[col].max())
                col_info["mean"] = round(float(df[col].mean()), 2)
            columns.append(col_info)

        return {
            "filename": filename,
            "rows": int(df.shape[0]),
            "columns_count": int(df.shape[1]),
            "columns": columns,
        }

    @staticmethod
    def build_prompt_schema(df: pd.DataFrame, filename: str) -> str:
        """
        Extract a text-based schema representation optimized for LLM prompting.
        """
        schema_lines = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            unique = df[col].nunique()
            schema_lines.append(f"  - {col} ({dtype}): {non_null} non-null, {unique} unique values")
            
            if df[col].dtype == "object" and unique <= 20:
                sample_vals = df[col].unique()[:10].tolist()
                schema_lines.append(f"    Sample values: {sample_vals}")
                
        return (
            f"Dataset: {filename}\n"
            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
            f"Columns:\n" + "\n".join(schema_lines)
        )
