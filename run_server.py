import uvicorn
from main import app # Assuming your FastAPI app instance is named 'app' in main.py

if __name__ == "__main__":
    print("DEBUG: run_server.py is starting Uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
    print("DEBUG: run_server.py: Uvicorn has finished.") # This line might not be reached if uvicorn.run blocks indefinitely