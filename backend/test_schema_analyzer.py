import pytest
import pandas as pd
import numpy as np
from schema_analyzer import SchemaAnalyzer

def test_schema_analyzer_extract():
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"],
        "C": [1.1, 2.2, 3.3]
    })
    
    schema = SchemaAnalyzer.extract_schema_dict(df, "test.csv")
    assert schema["filename"] == "test.csv"
    assert schema["rows"] == 3
    assert schema["columns_count"] == 3
    assert len(schema["columns"]) == 3
    
    col_a = next(c for c in schema["columns"] if c["name"] == "A")
    assert col_a["min"] == 1.0
    assert col_a["max"] == 3.0
    
    col_b = next(c for c in schema["columns"] if c["name"] == "B")
    assert "sample_values" in col_b

def test_schema_analyzer_nan():
    df = pd.DataFrame({
        "A": [np.nan, np.nan],
    })
    
    schema = SchemaAnalyzer.extract_schema_dict(df, "test.csv")
    col_a = next(c for c in schema["columns"] if c["name"] == "A")
    assert np.isnan(col_a["min"]) # min on all nan returns nan
