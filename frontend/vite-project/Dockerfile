# ====== Étape BUILD ======
FROM node:20-alpine AS build

WORKDIR /app

# Copie les fichiers essentiels pour l'installation
COPY package*.json ./
RUN npm install

# Copie les fichiers de configuration Tailwind et PostCSS
COPY tailwind.config.js postcss.config.js ./

# Copie le reste du code source
COPY . .

# 🔹 Variable d'environnement (facultative)
ENV DOCKER=true

# Lance le build
RUN npm run build


# ====== Étape NGINX ======
FROM nginx:stable-alpine

# Supprime la config Nginx par défaut et ajoute la tienne
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie les fichiers du build Vite dans le dossier de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
