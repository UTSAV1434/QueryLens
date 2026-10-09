import pytest
import pandas as pd
from query_executor import execute_pandas_query, dataframe_to_chart_data

def test_execute_pandas_query():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    code = "result_df = df[df['A'] > 1]"
    
    result = execute_pandas_query(df, code)
    assert len(result) == 2
    assert list(result["A"]) == [2, 3]

def test_execute_pandas_query_no_result_df():
    df = pd.DataFrame({"A": [1, 2, 3]})
    code = "wrong_var = df[df['A'] > 1]"
    
    with pytest.raises(RuntimeError, match="The generated code did not produce a 'result_df' variable"):
        execute_pandas_query(df, code)

def test_dataframe_to_chart_data():
    df = pd.DataFrame({"Category": ["A", "B"], "Value": [10, 20]})
    chart_data, y_cols = dataframe_to_chart_data(df, "Category", ["Value"])
    
    assert len(chart_data) == 2
    assert chart_data[0]["name"] == "A"
    assert chart_data[0]["Value"] == 10
    assert y_cols == ["Value"]
