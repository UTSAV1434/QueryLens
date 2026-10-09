# Domain Glossary

This file documents the core domain models and architectural seams in the project. Use these terms exactly when discussing the codebase.

## DatasetManager
The core interface responsible for tracking, caching, and serving loaded datasets on a per-session basis. It guarantees that concurrent users or browser tabs do not overwrite each other's data by keeping an in-memory `SessionCache`.

## SessionCache
The internal state mechanism within `DatasetManager` that maps a unique `session_id` (provided via the `X-Session-ID` HTTP header) to a specific user's loaded `DataFrame` and its computed schema.

## SchemaAnalyzer
A dedicated module that isolates pandas-specific data profiling and schema extraction logic. It prevents the presentation layer (Flask routes) from leaking into the domain logic when summarizing DataFrames for both JSON responses and LLM prompts.
