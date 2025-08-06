# Le Mixologue Augmenté - API Backend

## Description

API REST Flask pour "Le Mixologue Augmenté", une application de génération de cocktails personnalisés utilisant l'intelligence artificielle Mistral. Cette API permet de créer des fiches cocktails créatives basées sur les demandes des utilisateurs et de gérer un historique des créations.

## Architecture

- **Framework**: Flask (Python)
- **Base de données**: SQLite avec SQLAlchemy ORM
- **IA**: Mistral AI pour la génération de cocktails
- **CORS**: Configuré pour les applications frontend
- **Logging**: Système de logs intégré

## Installation et Configuration

### Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Clé API Mistral (obtenir sur [console.mistral.ai](https://console.mistral.ai/))

### Installation

1. **Cloner le projet et naviguer vers le backend**
   ```bash
   cd backend
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration des variables d'environnement**
   ```bash
   cp .env.example .env
   ```
   
   Éditer le fichier `.env` avec vos configurations :
   ```env
   # Configuration Flask
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=True
   
   # Configuration de la base de données
   DATABASE_URL=sqlite:///cocktails.db
   
   # Configuration CORS
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   
   # Configuration Mistral AI (OBLIGATOIRE)
   MISTRAL_API_KEY=votre_cle_api_mistral_ici
   MISTRAL_MODEL=mistral-large-latest
   
   # Configuration serveur
   HOST=localhost
   PORT=5000
   
   # Configuration de développement
   DEBUG_MODE=True
   LOG_LEVEL=INFO
   ```

4. **Démarrer l'application**
   ```bash
   python app.py
   ```

   L'API sera accessible sur `http://localhost:5000`

## Endpoints de l'API

### 1. Health Check

**GET** `/health`

Vérifie le statut de l'API.

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Le Mixologue Augmenté API"
}
```

### 2. Génération de Cocktail

**POST** `/api/cocktails/generate`

Génère un nouveau cocktail basé sur la demande de l'utilisateur.

**Corps de la requête :**
```json
{
  "prompt": "Je veux un cocktail fruité pour une soirée d'été"
}
```

**Réponse de succès (201) :**
```json
{
  "success": true,
  "cocktail": {
    "id": 1,
    "name": "Sunset Tropical",
    "ingredients": [
      "4 cl de rhum blanc",
      "2 cl de liqueur de passion",
      "6 cl de jus d'ananas",
      "2 cl de jus de citron vert",
      "1 trait de grenadine"
    ],
    "description": "Un cocktail qui capture l'essence d'un coucher de soleil tropical, avec ses saveurs fruitées et sa couleur dégradée.",
    "music_ambiance": "Musique lounge tropicale, sons de vagues en arrière-plan",
    "image_prompt": "Cocktail tropical dans un verre hurricane, couleurs dégradées orange-rouge, garni d'ananas et cerise, plage en arrière-plan, lumière dorée du coucher de soleil",
    "user_prompt": "Je veux un cocktail fruité pour une soirée d'été",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Erreurs possibles :**
- `400` : Champ "prompt" manquant ou vide
- `500` : Erreur lors de la génération ou de la sauvegarde

### 3. Liste des Cocktails (Historique)

**GET** `/api/cocktails`

Récupère la liste paginée des cocktails générés.

**Paramètres de requête :**
- `page` (optionnel) : Numéro de page (défaut: 1)
- `per_page` (optionnel) : Éléments par page (défaut: 10, max: 50)

**Exemple :** `/api/cocktails?page=1&per_page=5`

**Réponse :**
```json
{
  "cocktails": [
    {
      "id": 2,
      "name": "Midnight Velvet",
      "ingredients": ["..."],
      "description": "...",
      "music_ambiance": "...",
      "image_prompt": "...",
      "user_prompt": "...",
      "created_at": "2024-01-15T11:00:00.000Z"
    },
    {
      "id": 1,
      "name": "Sunset Tropical",
      "ingredients": ["..."],
      "description": "...",
      "music_ambiance": "...",
      "image_prompt": "...",
      "user_prompt": "...",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 5,
    "total": 2,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 4. Détails d'un Cocktail

**GET** `/api/cocktails/<int:cocktail_id>`

Récupère les détails d'un cocktail spécifique.

**Exemple :** `/api/cocktails/1`

**Réponse de succès :**
```json
{
  "cocktail": {
    "id": 1,
    "name": "Sunset Tropical",
    "ingredients": [
      "4 cl de rhum blanc",
      "2 cl de liqueur de passion",
      "6 cl de jus d'ananas",
      "2 cl de jus de citron vert",
      "1 trait de grenadine"
    ],
    "description": "Un cocktail qui capture l'essence d'un coucher de soleil tropical...",
    "music_ambiance": "Musique lounge tropicale, sons de vagues en arrière-plan",
    "image_prompt": "Cocktail tropical dans un verre hurricane...",
    "user_prompt": "Je veux un cocktail fruité pour une soirée d'été",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Erreur :**
- `404` : Cocktail non trouvé

## Modèle de Données

### Cocktail

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Identifiant unique (clé primaire) |
| `name` | String(200) | Nom créatif du cocktail |
| `ingredients` | Text (JSON) | Liste des ingrédients avec quantités |
| `description` | Text | Histoire/description du cocktail |
| `music_ambiance` | Text | Suggestion d'ambiance musicale |
| `image_prompt` | Text | Prompt pour génération d'image (optionnel) |
| `user_prompt` | Text | Demande originale de l'utilisateur |
| `created_at` | DateTime | Date de création |
| `updated_at` | DateTime | Date de dernière modification |

## Service Mistral AI

### Configuration

Le service utilise l'API Mistral pour générer des cocktails créatifs. Configuration requise :

- **MISTRAL_API_KEY** : Clé API obtenue sur [console.mistral.ai](https://console.mistral.ai/)
- **MISTRAL_MODEL** : Modèle utilisé (défaut: `mistral-large-latest`)

### Fonctionnement

1. **Prompt Système** : Définit le rôle de mixologue expert
2. **Prompt Utilisateur** : Intègre la demande du client
3. **Réponse Structurée** : JSON avec nom, ingrédients, description, ambiance musicale et prompt image
4. **Validation** : Vérification de la structure JSON retournée
5. **Fallback** : Génération de valeurs par défaut en cas d'erreur

### Gestion des Erreurs

- Retry automatique (3 tentatives max)
- Timeout de 30 secondes
- Logs détaillés pour le debugging
- Réponses de fallback en cas d'échec

## Gestion des Erreurs

### Codes de Statut HTTP

- `200` : Succès
- `201` : Création réussie
- `400` : Erreur de validation des données
- `404` : Ressource non trouvée
- `500` : Erreur interne du serveur

### Format des Erreurs

```json
{
  "error": "Description de l'erreur"
}
```

## Logging

Le système de logs capture :
- Requêtes de génération de cocktails
- Erreurs API Mistral
- Opérations de base de données
- Erreurs système

Niveau de log configurable via `LOG_LEVEL` dans `.env`.

## Sécurité

### CORS

Configuré pour accepter les requêtes depuis :
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (React dev server)

Modifiable via `CORS_ORIGINS` dans `.env`.

### Variables Sensibles

- Clé API Mistral stockée dans `.env`
- Secret Flask pour la sécurité des sessions
- Base de données locale (SQLite)

## Développement

### Structure du Projet

```
backend/
├── app.py              # Application Flask principale
├── models.py           # Modèles de données SQLAlchemy
├── services/
│   └── mistral_service.py  # Service d'intégration Mistral
├── requirements.txt    # Dépendances Python
├── .env.example       # Template de configuration
├── .env               # Configuration locale (à créer)
└── cocktails.db       # Base de données SQLite (générée)
```

### Tests

Pour tester l'API :

1. **Health Check**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Génération de cocktail**
   ```bash
   curl -X POST http://localhost:5000/api/cocktails/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Un cocktail épicé pour l'hiver"}'
   ```

3. **Liste des cocktails**
   ```bash
   curl http://localhost:5000/api/cocktails
   ```

### Débogage

- Logs disponibles dans la console
- Mode debug activé par défaut en développement
- Variables d'environnement pour ajuster le niveau de log

## Production

### Recommandations

1. **Sécurité**
   - Changer `SECRET_KEY` en production
   - Utiliser HTTPS
   - Configurer un reverse proxy (nginx)

2. **Base de données**
   - Migrer vers PostgreSQL ou MySQL
   - Configurer les sauvegardes

3. **Performance**
   - Utiliser un serveur WSGI (Gunicorn)
   - Configurer la mise en cache
   - Monitoring des performances

4. **Monitoring**
   - Logs centralisés
   - Métriques d'utilisation
   - Alertes sur les erreurs

## Support

Pour toute question ou problème :
1. Vérifier les logs de l'application
2. Valider la configuration des variables d'environnement
3. Tester la connectivité avec l'API Mistral
4. Consulter la documentation Mistral : [docs.mistral.ai](https://docs.mistral.ai/)

## Licence

Projet développé dans le cadre d'une évaluation technique.