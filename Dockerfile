# ========================
# Stage 1 : Build FRONTEND
# ========================
FROM node:20-alpine AS frontend
WORKDIR /frontend

# Copier uniquement package.json et package-lock.json pour profiter du cache
COPY frontend/package*.json ./
RUN npm install

# Copier le reste du frontend
COPY frontend/ .
RUN npm run build   # génère /frontend/dist

# ========================
# Stage 2 : Backend Python
# ========================
FROM python:3.11-slim
WORKDIR /app

# Copier backend
COPY backend/ /app/

# Copier le build frontend depuis le stage 1
COPY --from=frontend /frontend/dist /app/frontend/dist

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de FastAPI
EXPOSE 8000

# Lancer FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
