#!/bin/bash

# Script de démarrage Docker pour Le Mixologue Augmenté
# Ce script vérifie la configuration et démarre les services Docker

set -e  # Arrête le script en cas d'erreur

echo "🍸 Démarrage de Le Mixologue Augmenté avec Docker"
echo "================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
print_status "Vérification des prérequis..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que Docker est en cours d'exécution
if ! docker info &> /dev/null; then
    print_error "Docker n'est pas en cours d'exécution. Veuillez le démarrer."
    exit 1
fi

print_success "Docker est installé et en cours d'exécution"

# Vérification du fichier .env
if [ ! -f ".env" ]; then
    print_warning "Fichier .env non trouvé. Création à partir du template..."
    if [ -f ".env.docker" ]; then
        cp .env.docker .env
        print_warning "Fichier .env créé. ATTENTION: Modifiez les variables d'environnement avant la production!"
        print_warning "Notamment: SECRET_KEY, MISTRAL_API_KEY, DYNAPICTURES_API_KEY"
    else
        print_error "Template .env.docker non trouvé. Impossible de créer le fichier .env"
        exit 1
    fi
fi

# Vérification des clés API
print_status "Vérification de la configuration..."

source .env

if [ "$SECRET_KEY" = "your-secret-key-change-in-production-docker" ]; then
    print_warning "SECRET_KEY utilise la valeur par défaut. Changez-la en production!"
fi

if [ -z "$MISTRAL_API_KEY" ] || [ "$MISTRAL_API_KEY" = "your-mistral-api-key-here" ]; then
    print_warning "MISTRAL_API_KEY n'est pas configurée. La génération de cocktails ne fonctionnera pas."
fi

if [ -z "$DYNAPICTURES_API_KEY" ] || [ "$DYNAPICTURES_API_KEY" = "your-dynapictures-api-key-here" ]; then
    print_warning "DYNAPICTURES_API_KEY n'est pas configurée. La génération d'images ne fonctionnera pas."
fi

# Nettoyage des anciens conteneurs (optionnel)
if [ "$1" = "--clean" ]; then
    print_status "Nettoyage des anciens conteneurs..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f
fi

# Construction et démarrage des services
print_status "Construction des images Docker..."
if command -v docker-compose &> /dev/null; then
    docker-compose build --no-cache
else
    docker compose build --no-cache
fi

print_status "Démarrage des services..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# Attendre que les services soient prêts
print_status "Attente du démarrage des services..."
sleep 10

# Vérification de l'état des services
print_status "Vérification de l'état des services..."

# Vérifier le backend
if curl -f http://localhost:5001/health &> /dev/null; then
    print_success "Backend démarré avec succès (http://localhost:5001)"
else
    print_error "Le backend ne répond pas sur http://localhost:5001/health"
fi

# Vérifier le frontend
if curl -f http://localhost:80 &> /dev/null; then
    print_success "Frontend démarré avec succès (http://localhost:80)"
else
    print_error "Le frontend ne répond pas sur http://localhost:80"
fi

# Affichage des informations finales
echo ""
print_success "🎉 Le Mixologue Augmenté est démarré!"
echo ""
echo "📱 Application web: http://localhost:80"
echo "🔧 API Backend: http://localhost:5001"
echo "❤️  Health check: http://localhost:5001/health"
echo ""
print_status "Pour voir les logs: docker-compose logs -f"
print_status "Pour arrêter: docker-compose down"
print_status "Pour redémarrer proprement: ./docker-start.sh --clean"
echo ""
print_warning "N'oubliez pas de configurer vos clés API dans le fichier .env!"
echo "================================================="