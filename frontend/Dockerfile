# Stage 1: Build de l'application
FROM node:24-alpine AS builder

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de configuration des dépendances
COPY package*.json ./

# Installe les dépendances (y compris dev pour le build)
RUN npm ci

# Copie le code source
COPY . .

# Build l'application pour la production
RUN npm run build

# Stage 2: Serveur de production avec Nginx
FROM nginx:alpine

# Copie la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/nginx.conf

# Copie les fichiers buildés depuis le stage précédent
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose le port 80
EXPOSE 80

# Démarre Nginx
CMD ["nginx", "-g", "daemon off;"]