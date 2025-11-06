from fastapi import FastAPI
from bot_logic import hanja_def  # tes fonctions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔓 Autoriser les requêtes du frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:5173"] pour plus de sécurité
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API en ligne ✅"}

@app.get("/analyse")
async def analyse(text: str):
    result = await hanja_def(text)
    return {"input": text, "result": result}

#lancer l'API avec : uvicorn main:app --reload