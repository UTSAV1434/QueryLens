"""
LLM Engine - Translates natural language queries to pandas operations.
Uses OpenRouter API to access Gemini and other models.
Dynamically adapts to whatever dataset is currently loaded.
"""

import json
import re
import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-001"

MAX_RETRIES = 3
BASE_DELAY = 3


def build_system_prompt(schema_info: str, sample_rows: str) -> str:
    """Build a system prompt with the current dataset schema and sample data."""
    return f"""You are a data analysis assistant. You help users explore datasets by generating pandas code.

CURRENT DATASET SCHEMA:
{schema_info}

SAMPLE DATA (first 5 rows):
{sample_rows}

INSTRUCTIONS:
1. The user will ask questions about their data in natural language.
2. You must respond with a valid JSON object containing:
   - "pandas_code": A string of Python/pandas code that operates on a DataFrame called `df`. 
     The code MUST assign the final result to a variable called `result_df` (must be a DataFrame).
     Do NOT use print(). Do NOT import anything. Just write pandas operations.
     IMPORTANT: If the result needs aggregation, make sure the result_df has clear column names.
     If you use groupby, always reset_index() so the result is a flat DataFrame.
   - "chart_type": One of "bar", "line", "pie", "area", "table". Choose the most appropriate.
     Use "bar" for comparisons, "line" for time series/trends, "pie" for proportions (max 8 slices), 
     "area" for cumulative trends, "table" for detailed data.
   - "title": A short descriptive title for the chart/result.
   - "summary": A 1-2 sentence natural language summary explaining the insight from the data.
   - "x_column": The column name from result_df to use as the x-axis or label.
   - "y_columns": A list of column name(s) from result_df to use as y-axis values.

3. If the user's question cannot be answered with the available data, respond with:
   {{"error": "I cannot answer this question with the available data. The dataset contains: [list columns]."}}

4. IMPORTANT: Always respond with ONLY valid JSON. No markdown, no code blocks, no extra text.
5. Make sure column names in x_column and y_columns exactly match the columns in result_df.
6. For date/time based queries, parse the Date column to datetime first: df['Date'] = pd.to_datetime(df['Date'])
"""


def query_llm(user_query: str, schema_info: str, sample_rows: str) -> dict:
    """Send a natural language query via OpenRouter and get structured response with retry logic."""
    system_prompt = build_system_prompt(schema_info, sample_rows)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "QueryLens BI Dashboard",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User question: {user_query}"}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }

    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

            if response.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)
                    print(f"[LLM] Rate limited, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                return {"error": "API rate limit exceeded. Please try again in a moment."}

            if response.status_code != 200:
                return {"error": f"API error ({response.status_code}): {response.text[:200]}"}

            data = response.json()
            response_text = data["choices"][0]["message"]["content"].strip()

            # Try to extract JSON from the response
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response_text)
            if json_match:
                response_text = json_match.group(1).strip()

            parsed = json.loads(response_text)
            return parsed

        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse LLM response as JSON: {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else "No response"
            }
        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            if attempt < MAX_RETRIES - 1:
                time.sleep(BASE_DELAY)
                continue
        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(BASE_DELAY)
                continue
            return {"error": f"LLM query failed: {last_error}"}

    return {"error": f"LLM query failed after {MAX_RETRIES} retries: {last_error}"}
