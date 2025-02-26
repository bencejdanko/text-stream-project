from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
import aiofiles
import os
import argparse

app = FastAPI()

# Default values
DATA_DIR = "data"
CHUNK_SIZE = 1024

async def read_file_stream(file_path: str):
    """Asynchronous generator that reads small chunks of a file and streams JSON."""
    async with aiofiles.open(file_path, mode="r") as file:
        while True:
            chunk = await file.read(CHUNK_SIZE)  # Read small chunks
            if not chunk:
                break  # Stop when file ends
            yield json.dumps({
                "chunk": chunk
            }) + "\n"
            await asyncio.sleep(0)  # Allow async event loop to process requests

@app.get("/list_files")
async def list_md_files():
    """Endpoint to list all .md files in the data directory."""
    try:
        files = [f for f in os.listdir(DATA_DIR)]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/{filename}")
async def stream_logs(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return StreamingResponse(read_file_stream(file_path), media_type="application/json")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run FastAPI server with custom settings.")
    parser.add_argument("--data-dir", type=str, help="Directory to read data files from.")
    parser.add_argument("--chunk-size", type=int, help="Size of chunks to read from files.")
    parser.add_argument("--port", type=int, help="Port to run the server on.")
    args = parser.parse_args()

    # Update variables based on arguments
    DATA_DIR = args.data_dir
    CHUNK_SIZE = args.chunk_size
    PORT = args.port

    if not DATA_DIR or not CHUNK_SIZE or not PORT:
        raise ValueError("Please provide both --data-dir and --chunk-size arguments.")

    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)