"""
HTTP_handler.py

This is a lightweight FastAPI server that allows Roblox Studio
to request indexed part data stored in `queued_parts.txt`.

Usage:
    Run HTTP_handler.py file then run the place in Roblox Studios.

By default, the server is hosted locally on:
    http://127.0.0.1:8000

The endpoint `/get` returns the contents of `queued_parts.txt`
as a list of lines, which can then be parsed by the Roblox
`PartPlacer.lua` script.
"""

import uvicorn
from fastapi import FastAPI
from config import QUEUED_PATH

app = FastAPI()

# Endpoint: http://127.0.0.1:8000/get
# Returns the queued parts to Roblox Studio when requested.
@app.get("/get")
def send_parts() -> list[str]:
    return QUEUED_PATH.read_text().splitlines()

def start_dev_server():
    """
    Runs the API server.
    Pressing CTRL+C will stop the server and let the thread continue
    """

    # basic check, if it fails there's no point in starting it.
    if not QUEUED_PATH.exists():
        print(f"Cannot start API server because no file was found at {QUEUED_PATH}")
        return
    
    try:
        uvicorn.run(app)
    except KeyboardInterrupt:
        # in case the user pressed ctrl+c extra times
        ...

if __name__ == "__main__":
    start_dev_server()