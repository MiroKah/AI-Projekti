# =============================================================================
# StudyAI Frontend — Dockerfile (kehitys)
# =============================================================================
FROM node:22-alpine

WORKDIR /app

# --- Riippuvuudet (välimuisti hyödyntäen) ---
COPY package.json package-lock.json* ./
RUN npm install

# --- Sovelluskoodi ---
COPY . .

EXPOSE 3000

# Kehityspalvelin
CMD ["npm", "run", "dev"]