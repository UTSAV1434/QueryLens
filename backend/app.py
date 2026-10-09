"""
Flask API - Main application for the Conversational BI Dashboard.
Supports any CSV dataset upload and natural language querying via Gemini.
"""

import os
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from llm_engine import query_llm
from query_executor import execute_pandas_query, dataframe_to_chart_data
from data_manager import DatasetManager
from schema_analyzer import SchemaAnalyzer

load_dotenv()


app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global singleton DatasetManager to handle all sessions
dataset_manager = DatasetManager()

def get_session_id():
    """Extract session ID from headers or fallback to a default."""
    return request.headers.get("X-Session-ID", "default_session")

# Load default sample dataset on startup for the default session
default_csv = os.path.join(DATA_DIR, "sample_sales_data.csv")
if os.path.exists(default_csv):
    dataset_manager.load_dataset("default_session", default_csv, "sample_sales_data.csv")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    session_id = get_session_id()
    data = dataset_manager.get_session_data(session_id)
    return jsonify({
        "status": "ok",
        "dataset_loaded": data is not None,
        "dataset_name": data["filename"] if data else None,
        "session_id": session_id
    })


@app.route("/api/schema", methods=["GET"])
def schema():
    session_id = get_session_id()
    data = dataset_manager.get_session_data(session_id)
    
    if not data or data["df"] is None:
        return jsonify({"error": "No dataset loaded for this session. Please upload a CSV file."}), 400

    df = data["df"]
    schema_dict = SchemaAnalyzer.extract_schema_dict(df, data["filename"])
    return jsonify(schema_dict)


@app.route("/api/query", methods=["POST"])
def query():
    session_id = get_session_id()
    data = dataset_manager.get_session_data(session_id)
    
    if not data or data["df"] is None:
        return jsonify({"error": "No dataset loaded. Please upload a CSV file first."}), 400

    req_data = request.get_json()
    if not req_data or "query" not in req_data:
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    user_query = req_data["query"].strip()
    if not user_query:
        return jsonify({"error": "Query cannot be empty."}), 400

    # Step 1: Ask Gemini to generate pandas code
    llm_response = query_llm(
        user_query,
        data["schema_info"],
        data["sample_rows"]
    )

    if "error" in llm_response:
        return jsonify({
            "error": llm_response["error"],
            "type": "llm_error"
        }), 200

    # Step 2: Execute the pandas code
    try:
        result_df = execute_pandas_query(
            data["df"],
            llm_response.get("pandas_code", "")
        )
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "type": "execution_error",
            "pandas_code": llm_response.get("pandas_code", ""),
        }), 200

    # Step 3: Convert to chart data
    x_column = llm_response.get("x_column", result_df.columns[0])
    y_columns = llm_response.get("y_columns", list(result_df.columns[1:]))

    try:
        chart_data, actual_y_columns = dataframe_to_chart_data(result_df, x_column, y_columns)
    except Exception as e:
        return jsonify({
            "error": f"Failed to format chart data: {str(e)}",
            "type": "format_error",
        }), 200

    return jsonify({
        "chart_data": chart_data,
        "chart_type": llm_response.get("chart_type", "bar"),
        "title": llm_response.get("title", "Query Result"),
        "summary": llm_response.get("summary", ""),
        "x_column": x_column,
        "y_columns": actual_y_columns,
        "rows_returned": len(chart_data),
    })


@app.route("/api/upload", methods=["POST"])
def upload():
    session_id = get_session_id()
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Please upload a CSV file."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported."}), 400

    # Save the file
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)

    # Load into memory using DatasetManager
    try:
        dataset_manager.load_dataset(session_id, filepath, file.filename)
    except Exception as e:
        return jsonify({"error": f"Failed to load CSV: {str(e)}"}), 400

    df = dataset_manager.get_dataframe(session_id)
    return jsonify({
        "message": f"Successfully loaded '{file.filename}'",
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
    })


@app.route("/api/datasets", methods=["GET"])
def list_datasets():
    """List available datasets in the data directory."""
    session_id = get_session_id()
    datasets = []

    # Check data dir
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".csv"):
                datasets.append({"name": f, "source": "built-in"})

    # Check uploads dir
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith(".csv"):
                datasets.append({"name": f, "source": "uploaded"})

    data = dataset_manager.get_session_data(session_id)
    return jsonify({
        "datasets": datasets,
        "current": data["filename"] if data else None,
    })


@app.route("/api/datasets/load", methods=["POST"])
def load_existing_dataset():
    """Load an existing dataset by name."""
    session_id = get_session_id()
    req_data = request.get_json()
    if not req_data or "filename" not in req_data:
        return jsonify({"error": "Missing 'filename' field."}), 400

    filename = req_data["filename"]

    # Search in data dir first, then uploads
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": f"File '{filename}' not found."}), 404

    try:
        dataset_manager.load_dataset(session_id, filepath, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to load: {str(e)}"}), 400

    df = dataset_manager.get_dataframe(session_id)
    return jsonify({
        "message": f"Loaded '{filename}'",
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
