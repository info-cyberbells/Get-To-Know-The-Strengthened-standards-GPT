import subprocess
import sys
import os
from threading import Thread

def run_backend():
    # Run FastAPI with hot reload
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "backend.app:app", 
        "--reload",  # Enable hot reload
        "--host", "127.0.0.1", 
        "--port", "8000"
    ])

def run_frontend():
    # Run a simple HTTP server for the frontend with auto-reload
    subprocess.run([
        sys.executable, "-m", "http.server", 
        "--directory", "frontend", 
        "3000"
    ])

if __name__ == "__main__":
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()

    # Start frontend server
    run_frontend()
