from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from .bot_logic import hanja_def

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

# 🔍 TEST : afficher le chemin dans les logs Railway
print(">>> FRONTEND PATH =", frontend_path)
print(">>> exists:", os.path.isdir(frontend_path))
print(">>> content:", os.listdir(os.path.dirname(frontend_path)) if os.path.isdir(os.path.dirname(frontend_path)) else "no parent dir")


# API
@app.get("/analyse")
async def analyse(text: str):
    result = await hanja_def(text)
    return {"input": text, "result": result}
