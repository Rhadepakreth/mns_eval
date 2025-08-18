#!/bin/bash

# Script d'arrêt Docker pour Le Mixologue Augmenté
# Ce script arrête proprement les services Docker

set -e  # Arrête le script en cas d'erreur

echo "🛑 Arrêt de Le Mixologue Augmenté"
echo "================================="

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

# Vérifier que Docker Compose est disponible
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose n'est pas installé."
    exit 1
fi

# Arrêt des services selon l'option choisie
case "$1" in
    --clean)
        print_status "Arrêt et nettoyage complet des services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down --volumes --remove-orphans
        else
            docker compose down --volumes --remove-orphans
        fi
        
        print_status "Suppression des images Docker..."
        docker rmi $(docker images "mns_eval*" -q) 2>/dev/null || true
        
        print_status "Nettoyage du système Docker..."
        docker system prune -f
        
        print_success "Nettoyage complet terminé"
        ;;
    
    --volumes)
        print_status "Arrêt des services avec suppression des volumes..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down --volumes
        else
            docker compose down --volumes
        fi
        print_warning "Les données de la base de données ont été supprimées"
        ;;
    
    --force)
        print_status "Arrêt forcé des services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose kill
            docker-compose down --remove-orphans
        else
            docker compose kill
            docker compose down --remove-orphans
        fi
        print_success "Arrêt forcé terminé"
        ;;
    
    *)
        print_status "Arrêt normal des services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down
        else
            docker compose down
        fi
        print_success "Services arrêtés"
        ;;
esac

# Vérification que les conteneurs sont bien arrêtés
running_containers=$(docker ps --filter "name=mixologue" --format "table {{.Names}}" | grep -v NAMES | wc -l)

if [ "$running_containers" -eq 0 ]; then
    print_success "✅ Tous les conteneurs Le Mixologue Augmenté sont arrêtés"
else
    print_warning "⚠️  Certains conteneurs sont encore en cours d'exécution:"
    docker ps --filter "name=mixologue" --format "table {{.Names}}\t{{.Status}}"
fi

echo ""
echo "Options disponibles:"
echo "  ./docker-stop.sh          - Arrêt normal"
echo "  ./docker-stop.sh --clean  - Arrêt + nettoyage complet"
echo "  ./docker-stop.sh --volumes - Arrêt + suppression des volumes"
echo "  ./docker-stop.sh --force   - Arrêt forcé"
echo ""
print_status "Pour redémarrer: ./docker-start.sh"
echo "================================="