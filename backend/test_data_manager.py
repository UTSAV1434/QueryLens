import pytest
import pandas as pd
import os
from data_manager import DatasetManager

def test_dataset_manager(tmp_path):
    manager = DatasetManager()
    session_id = "test_session"
    
    # Create a dummy csv
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("A,B\n1,2\n3,4")
    
    manager.load_dataset(session_id, str(csv_file), "test.csv")
    
    assert manager.has_dataset(session_id)
    df = manager.get_dataframe(session_id)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["A", "B"]
    
    data = manager.get_session_data(session_id)
    assert data["filename"] == "test.csv"
    assert "schema_info" in data
    assert "sample_rows" in data
    assert "last_accessed" in data

def test_dataset_manager_expiry(tmp_path):
    manager = DatasetManager(expiry_seconds=0.1) # 100ms expiry
    
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("A,B\n1,2\n3,4")
    
    manager.load_dataset("session1", str(csv_file), "test.csv")
    assert manager.has_dataset("session1")
    
    import time
    time.sleep(0.2)
    
    # This should trigger cleanup
    assert manager.get_session_data("session1") is None
    assert not manager.has_dataset("session1")

def test_dataset_manager_preserves_default(tmp_path):
    manager = DatasetManager(expiry_seconds=0.1)
    
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("A,B\n1,2\n3,4")
    
    manager.load_dataset("default_session", str(csv_file), "test.csv")
    
    import time
    time.sleep(0.2)
    
    manager._cleanup_expired_sessions()
    assert manager.has_dataset("default_session")
