from fastapi import FastAPI

# Run this in terminal:
"""
fastapi dev .\HTTP_handler.py
"""

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get")
def read_item():

    queued_parts = list()
    with open("current/queued_parts.txt", 'r') as f:
        for line in f:
            queued_parts.append(line)
    return queued_parts


"""
{
    [
        <part_data + uncertainties>,
        ...
    ]
}
"""