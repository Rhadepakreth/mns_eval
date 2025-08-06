# Cahier des Charges - Le Mixologue Augmenté

## Contexte du Projet

Vous êtes chargé de développer une application web d'aide à la création de cocktails pour Arnaud Dumas, gérant d'un bar à cocktails à Metz. L'objectif est de créer une solution IA qui génère des fiches cocktails personnalisées selon les demandes des clients, permettant aux barmans de proposer rapidement des créations originales.

## Spécifications Fonctionnelles

### Fonctionnalité Principale
- **Générateur de cocktails IA** : Interface permettant de saisir une demande textuelle libre et obtenir une fiche cocktail complète

### Contenu des Fiches Cocktails Générées
Chaque fiche doit obligatoirement contenir :
1. **Nom du cocktail** : Création originale et créative de l'IA
2. **Liste complète des ingrédients** avec quantités précises
3. **Histoire/description courte** du cocktail (contexte, inspiration)
4. **Suggestion d'ambiance musicale** adaptée au cocktail
5. **Prompt image** (optionnel) pour MidJourney/SDXL

### Gestion des Données
- **Historisation** : Sauvegarde automatique de toutes les fiches générées
- **Consultation** : Interface pour parcourir et consulter les fiches précédentes
- **Persistance** : Les données doivent être conservées en base de données

## Spécifications Techniques

### Architecture Obligatoire
- **Backend** : Django OU Flask (justifier le choix dans le README)
- **Frontend** : React avec Vite + TailwindCSS 4
- **Base de données** : SQLite (développement)
- **IA** : Modèle Mistral via API (clé stockée en variable d'environnement)

### Contraintes de Déploiement
- **Containerisation** : Application entièrement dockerisée
- **Configuration** : Variables d'environnement documentées
- **Déploiement** : Prêt pour serveur de production

## Exemples de Prompts Utilisateur

L'application doit gérer des demandes variées comme :
- "J'ai envie de quelque chose de fruité mais avec du gin, et pas trop sucré"
- "Un cocktail sans alcool pour une après-midi en terrasse"
- "Une création originale à base de whisky et citron vert"
- "Je suis de bonne humeur et il fait beau aujourd'hui, tu me conseilles de boire quoi ?"

## Interface Utilisateur

### Page Principale - Génération
- Champ de saisie libre pour la demande
- Bouton de génération
- Zone d'affichage de la fiche générée
- Options de sauvegarde

### Page Historique
- Liste des cocktails précédemment générés
- Fonction de recherche/filtrage
- Affichage détaillé de chaque fiche

### Design et Framework CSS
- **Frontend** : React avec Vite
- **Styling** : TailwindCSS 4
- **Architecture** : SPA (Single Page Application) avec API REST backend

## Livrables Attendus

### Code Source
- Repository GitHub complet et fonctionnel
- Structure de projet claire (backend + frontend séparés)
- Code commenté et documenté

### Documentation (README.md)
1. **Justification des choix techniques**
   - Framework backend choisi (Django vs Flask)
   - Choix React + Vite pour le frontend
   - Sélection du modèle Mistral utilisé
2. **Guide d'installation détaillé**
   - Prérequis système
   - Installation backend et frontend
   - Configuration des variables d'environnement
3. **Documentation des variables configurables**
   - Variables d'environnement (.env)
   - Configuration API Mistral (MISTRAL_API_KEY, modèle)
   - Paramètres base de données SQLite

---

## Liste des Tâches à Exécuter

### Phase 1 : Setup et Architecture
- [ ] Choisir et justifier le framework backend (Django/Flask)
- [ ] Initialiser le repository Git avec structure backend/frontend
- [ ] Configurer le backend (Python + environnement virtuel)
- [ ] Initialiser React + Vite pour le frontend
- [ ] Configurer TailwindCSS 4
- [ ] Sélectionner le modèle Mistral optimal (mistral-large, mistral-medium)
- [ ] Configurer les variables d'environnement (.env)

### Phase 2 : Backend - Modèles et Base de Données
- [ ] Configurer SQLite pour le développement
- [ ] Définir le modèle de données pour les cocktails
- [ ] Créer les migrations
- [ ] Implémenter les modèles (Cocktail, Ingrédient, etc.)
- [ ] Tester les modèles en console

### Phase 3 : Intégration IA Mistral
- [ ] Configurer l'accès API Mistral avec variable d'environnement
- [ ] Créer le fichier .env avec MISTRAL_API_KEY
- [ ] Créer le service de génération de cocktails (appels API Mistral)
- [ ] Développer le prompt système optimisé pour Mistral
- [ ] Tester et optimiser les réponses de l'API Mistral
- [ ] Gérer les erreurs et timeouts API Mistral

### Phase 4 : Backend - API REST
- [ ] Créer l'API REST pour la génération de cocktails
- [ ] Endpoint POST /api/cocktails/generate
- [ ] Endpoint GET /api/cocktails (historique)
- [ ] Endpoint GET /api/cocktails/:id (détail)
- [ ] Gérer CORS pour React
- [ ] Valider les données d'entrée

### Phase 5 : Frontend React
- [ ] Configurer le routing React (React Router)
- [ ] Créer les composants de base avec TailwindCSS 4
- [ ] Page génération de cocktails (formulaire + affichage)
- [ ] Page historique avec liste des cocktails
- [ ] Page détail d'un cocktail
- [ ] Gérer les états de chargement et erreurs
- [ ] Responsive design (mobile/tablette)
- [ ] Intégrer les appels API

### Phase 6 : Tests et Optimisation
- [ ] Tests unitaires backend
- [ ] Tests d'intégration API Mistral
- [ ] Tests fonctionnels interface
- [ ] Optimisation des performances
- [ ] Validation avec différents types de demandes
- [ ] Test des limites de l'API Mistral

### Phase 7 : Dockerisation
- [ ] Créer le Dockerfile pour le backend
- [ ] Créer le Dockerfile pour le frontend (build + serve)
- [ ] Configurer docker-compose.yml (backend + frontend)
- [ ] Gérer les variables d'environnement (.env pour Mistral)
- [ ] Tester le déploiement Docker complet
- [ ] Optimiser les images Docker

### Phase 8 : Documentation et Finalisation
- [ ] Rédiger le README complet
- [ ] Documenter les variables d'environnement
- [ ] Créer le guide d'installation
- [ ] Justifier les choix techniques
- [ ] Vérifier la conformité au cahier des charges
- [ ] Tests finaux et validation

### Phase 9 : Livraison
- [ ] Push final du code sur GitHub
- [ ] Vérification de la documentation
- [ ] Test de déploiement depuis zéro (backend + frontend)
- [ ] Validation finale des fonctionnalités

---

## Notes Importantes pour l'IA d'IDE

- **Architecture découplée** : Backend API REST + Frontend React SPA
- **API Mistral obligatoire** : Utiliser l'API Mistral avec clé en variable d'environnement
- **Configuration .env** : MISTRAL_API_KEY indispensable pour le fonctionnement
- **Prioriser la qualité des réponses** : Optimiser les prompts pour Mistral
- **Respecter les contraintes techniques** : Django/Flask + Docker + React obligatoires
- **Base SQLite** : Simple pour le développement, facilite le setup
- **TailwindCSS 4** : Utiliser les dernières fonctionnalités pour un design moderne
- **Documentation essentielle** : Guide d'installation détaillé indispensable
- **Historisation critique** : Fonctionnalité métier importante pour le gérant