#!/usr/bin/env python3
"""
Main entry point for the RAG application.
This file runs the Streamlit frontend.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit frontend application."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the frontend file
    frontend_path = os.path.join(script_dir, "app", "frontend", "frontend.py")
    
    # Check if the frontend file exists
    if not os.path.exists(frontend_path):
        print(f"Error: Frontend file not found at {frontend_path}")
        sys.exit(1)
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", frontend_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
