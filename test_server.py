# -*- coding: utf-8 -*-
"""Simple test server to debug API issues"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/test")
async def test(data: dict):
    return {"received": data}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
