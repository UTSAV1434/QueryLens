import sys
import os

# Add the backend directory to the Python path so local imports work
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_dir)

# Import the Flask app
from app import app
