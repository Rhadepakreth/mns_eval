# 🐳 Déploiement Docker - Le Mixologue Augmenté

Ce guide vous explique comment déployer l'application "Le Mixologue Augmenté" avec Docker et Docker Compose.

## 📋 Prérequis

- **Docker** (version 20.10 ou supérieure)
- **Docker Compose** (version 2.0 ou supérieure)
- **8 GB de RAM** minimum recommandé
- **2 GB d'espace disque** libre

### Installation de Docker

#### macOS
```bash
# Avec Homebrew
brew install --cask docker

# Ou téléchargez Docker Desktop depuis https://docker.com
```

#### Linux (Ubuntu/Debian)
```bash
# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation de Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🚀 Démarrage rapide

### 1. Configuration des variables d'environnement

```bash
# Copiez le template de configuration
cp .env.docker .env

# Éditez le fichier .env avec vos clés API
nano .env  # ou votre éditeur préféré
```

**Variables importantes à configurer :**

```bash
# Clé secrète Flask (OBLIGATOIRE à changer en production)
SECRET_KEY=votre-cle-secrete-unique

# Clés API des services externes
MISTRAL_API_KEY=votre-cle-mistral
DYNAPICTURES_API_KEY=votre-cle-dynapictures

# Configuration CORS (adaptez à votre domaine)
CORS_ORIGINS=http://localhost:80,https://votre-domaine.com
```

### 2. Démarrage de l'application

```bash
# Démarrage simple
./docker-start.sh

# Ou démarrage avec nettoyage préalable
./docker-start.sh --clean
```

### 3. Accès à l'application

- **Application web** : http://localhost:80
- **API Backend** : http://localhost:5001
- **Health check** : http://localhost:5001/health

## 🏗️ Architecture Docker

### Services déployés

1. **Frontend** (`mixologue_frontend`)
   - **Image** : Nginx + React/Vite build
   - **Port** : 80
   - **Rôle** : Interface utilisateur et reverse proxy

2. **Backend** (`mixologue_backend`)
   - **Image** : Python 3.11 + Flask
   - **Port** : 5001
   - **Rôle** : API REST et logique métier

3. **Réseau** (`mixologue_network`)
   - Communication interne entre les services

### Volumes persistants

- `./backend/cocktails.db` : Base de données SQLite
- `./backend/static` : Images générées des cocktails

## 🛠️ Commandes utiles

### Gestion des services

```bash
# Démarrer les services
./docker-start.sh

# Arrêter les services
./docker-stop.sh

# Arrêt avec nettoyage complet
./docker-stop.sh --clean

# Arrêt forcé
./docker-stop.sh --force
```

### Monitoring et debugging

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend

# État des conteneurs
docker-compose ps

# Statistiques d'utilisation
docker stats
```

### Maintenance

```bash
# Reconstruire les images
docker-compose build --no-cache

# Redémarrer un service
docker-compose restart backend

# Accéder au shell d'un conteneur
docker-compose exec backend bash
docker-compose exec frontend sh

# Sauvegarder la base de données
docker cp mixologue_backend:/app/cocktails.db ./backup_$(date +%Y%m%d_%H%M%S).db
```

## 🔧 Configuration avancée

### Variables d'environnement complètes

```bash
# Sécurité
SECRET_KEY=votre-cle-secrete-unique
FLASK_ENV=production
FLASK_DEBUG=False

# Services externes
MISTRAL_API_KEY=votre-cle-mistral
DYNAPICTURES_API_KEY=votre-cle-dynapictures

# Réseau
CORS_ORIGINS=http://localhost:80,https://votre-domaine.com
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Limitation de taux
RATE_LIMIT_GENERATE=5
RATE_LIMIT_API=100
RATE_LIMIT_STATIC=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

### Personnalisation des ports

Modifiez le fichier `docker-compose.yml` :

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Application accessible sur le port 8080
  
  backend:
    ports:
      - "8001:5001"  # API accessible sur le port 8001
```

### Migration vers PostgreSQL

Décommentez la section PostgreSQL dans `docker-compose.yml` :

```yaml
db:
  image: postgres:15-alpine
  container_name: mixologue_db
  environment:
    POSTGRES_DB: mixologue
    POSTGRES_USER: mixologue_user
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

Et ajoutez dans `.env` :

```bash
DB_PASSWORD=mot-de-passe-securise
DATABASE_URL=postgresql://mixologue_user:${DB_PASSWORD}@db:5432/mixologue
```

## 🚀 Déploiement en production

### 1. Sécurisation

```bash
# Générer une clé secrète sécurisée
python -c "import secrets; print(secrets.token_hex(32))"

# Mettre à jour .env avec la nouvelle clé
SECRET_KEY=la-cle-generee-ci-dessus
FLASK_DEBUG=False
FLASK_ENV=production
```

### 2. Reverse proxy (recommandé)

Ajoutez un reverse proxy Nginx pour HTTPS :

```nginx
server {
    listen 443 ssl http2;
    server_name votre-domaine.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Monitoring

Ajoutez des health checks et monitoring :

```bash
# Vérification automatique de santé
watch -n 30 'curl -f http://localhost:5001/health || echo "Service DOWN"'

# Logs rotatifs
docker-compose logs --tail=1000 > logs/app_$(date +%Y%m%d).log
```

## 🐛 Dépannage

### Problèmes courants

#### Port déjà utilisé
```bash
# Identifier le processus utilisant le port
lsof -i :80
lsof -i :5001

# Arrêter le processus ou changer le port dans docker-compose.yml
```

#### Problème de permissions
```bash
# Corriger les permissions des scripts
chmod +x docker-start.sh docker-stop.sh

# Corriger les permissions des volumes
sudo chown -R $USER:$USER ./backend/static
```

#### Erreur de build
```bash
# Nettoyer le cache Docker
docker system prune -a

# Reconstruire sans cache
docker-compose build --no-cache
```

#### Services qui ne démarrent pas
```bash
# Vérifier les logs détaillés
docker-compose logs backend
docker-compose logs frontend

# Vérifier la configuration
docker-compose config
```

### Logs et debugging

```bash
# Logs en temps réel avec timestamps
docker-compose logs -f -t

# Logs des dernières 100 lignes
docker-compose logs --tail=100

# Exporter les logs
docker-compose logs > debug_logs.txt
```

## 📊 Performance et optimisation

### Ressources recommandées

- **CPU** : 2 cores minimum, 4 cores recommandé
- **RAM** : 4 GB minimum, 8 GB recommandé
- **Stockage** : 10 GB minimum pour les images et logs

### Optimisations

```bash
# Limiter la mémoire des conteneurs
docker-compose.yml:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Sauvegarde automatique

```bash
# Script de sauvegarde quotidienne
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
docker cp mixologue_backend:/app/cocktails.db $BACKUP_DIR/

# Sauvegarder les images
cp -r ./backend/static $BACKUP_DIR/

# Nettoyer les anciennes sauvegardes (garder 7 jours)
find ./backups -type d -mtime +7 -exec rm -rf {} +
```

## 🆘 Support

En cas de problème :

1. Consultez les logs : `docker-compose logs`
2. Vérifiez la configuration : `docker-compose config`
3. Testez les health checks : `curl http://localhost:5001/health`
4. Redémarrez proprement : `./docker-stop.sh --clean && ./docker-start.sh`

---

**🍸 Bon déploiement avec Le Mixologue Augmenté !**