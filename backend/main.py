from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from bot_logic import hanja_def

app = FastAPI(title="Hanja App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 Chemin correct vers le build du front
frontend_path = os.path.join(os.path.dirname(__file__), "frontend/dist")

# 🚀 Sert TOUT le front (index.html + assets)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# API
@app.get("/analyse")
async def analyse(text: str):
    result = await hanja_def(text)
    return {"input": text, "result": result}
