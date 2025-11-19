from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
#from backend.bot_logic import hanja_def  # a utiliser en local
from bot_logic import hanja_def

app = FastAPI(title="Hanja App")

# 🔓 Autoriser le front à appeler l'API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # mettre le domaine en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Chemin absolu vers le dossier dist
frontend_path = os.path.join(os.path.dirname(__file__), "frontend/dist")

# 🔹 Monte le build complet (JS, CSS, index.html, etc.)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# 🔹 Route API pour l'analyse
@app.get("/analyse")
async def analyse(text: str):
    result = await hanja_def(text)
    return {"input": text, "result": result}



# Pour exécuter avec: uvicorn backend.main:app --reload
