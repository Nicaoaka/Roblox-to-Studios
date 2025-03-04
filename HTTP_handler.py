from typing import Union
from fastapi import FastAPI



app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get")
def read_item():

    queued_parts = list()
    with open("queued_parts.csv", 'r') as f:
        for line in f:
            queued_parts.append(line)
    return queued_parts


"""
{
    [
        "<.csv string>",
        ...
    ]
}
"""