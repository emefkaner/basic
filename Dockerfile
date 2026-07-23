# Schlankes Node-Image + system-ffmpeg (robuster als Binär-Download zur Build-Zeit).
FROM node:20-slim

# ffmpeg für Audio-Zusammenschnitt, -Optimierung und -Analyse.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Abhängigkeiten zuerst (besseres Layer-Caching).
COPY package.json ./
RUN npm install --omit=dev

# Restlichen Code kopieren.
COPY . .

# Datenordner (wird auf Render/Railway idealerweise auf ein Volume gemountet).
ENV DATA_DIR=/data
RUN mkdir -p /data

EXPOSE 3000
CMD ["node", "src/server.js"]
