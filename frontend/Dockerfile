FROM node:20-alpine

WORKDIR /app

# Copier uniquement package.json et package-lock.json pour profiter du cache
COPY package.json package-lock.json ./

# Installer les dépendances
RUN npm install

# Copier le reste des fichiers
COPY . .

# Build Vite app
RUN npm run build

# Installer un serveur léger
RUN npm install -g serve

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]