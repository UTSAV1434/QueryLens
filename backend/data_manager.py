import os
import time
import pandas as pd
from typing import Dict, Any

from schema_analyzer import SchemaAnalyzer

class DatasetManager:
    """
    Manages datasets for multiple concurrent sessions.
    Deep module that encapsulates pandas loading, schema extraction, and in-memory caching.
    """
    
    def __init__(self, expiry_seconds: int = 3600):
        # Maps session_id -> { "df": pd.DataFrame, "filename": str, "schema_info": str, "sample_rows": str, "last_accessed": float }
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.expiry_seconds = expiry_seconds

    def _cleanup_expired_sessions(self):
        """Remove sessions that haven't been accessed within the expiry window."""
        current_time = time.time()
        expired_sessions = [
            sid for sid, data in self._sessions.items()
            if current_time - data.get("last_accessed", current_time) > self.expiry_seconds
        ]
        for sid in expired_sessions:
            # We skip 'default_session' so the sample dataset remains available
            if sid != "default_session":
                del self._sessions[sid]
        
    def load_dataset(self, session_id: str, filepath: str, filename: str) -> None:
        """Load a CSV file into the session cache and extract its schema."""
        df = pd.read_csv(filepath)
        
        # Build schema info string using SchemaAnalyzer
        schema_info = SchemaAnalyzer.build_prompt_schema(df, filename)
        sample_rows = df.head(5).to_string(index=False)

        
        self._cleanup_expired_sessions()
        
        self._sessions[session_id] = {
            "df": df,
            "filename": filename,
            "schema_info": schema_info,
            "sample_rows": sample_rows,
            "last_accessed": time.time()
        }
        
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Retrieve the dataset dictionary for a session and update access time."""
        self._cleanup_expired_sessions()
        if session_id in self._sessions:
            self._sessions[session_id]["last_accessed"] = time.time()
            return self._sessions[session_id]
        return None
        
    def has_dataset(self, session_id: str) -> bool:
        """Check if a session has a loaded dataset."""
        return session_id in self._sessions and self._sessions[session_id]["df"] is not None
        
    def get_dataframe(self, session_id: str) -> pd.DataFrame:
        """Get the pandas DataFrame for a session."""
        data = self.get_session_data(session_id)
        return data["df"] if data else None
