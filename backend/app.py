#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Le Mixologue Augmenté - Backend Flask

Application Flask pour la génération de cocktails avec IA Mistral.
Fournit une API REST pour le frontend React.

Auteur: Assistant IA
Date: 2024
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging
from datetime import datetime

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de l'application
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cocktails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration CORS pour permettre les requêtes depuis React
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=cors_origins)

# Initialisation de la base de données
db = SQLAlchemy(app)

# Import des modèles après initialisation de db
import models
Cocktail = models.create_models(db)

# Import des services
from services.mistral_service import MistralService

# Initialisation du service Mistral
mistral_service = MistralService()

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé de l'API.
    
    Returns:
        dict: Statut de l'application et timestamp
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Le Mixologue Augmenté API'
    })

@app.route('/api/cocktails/generate', methods=['POST'])
def generate_cocktail():
    """
    Génère un nouveau cocktail basé sur la demande de l'utilisateur.
    
    Expected JSON payload:
        {
            "prompt": "Description de la demande utilisateur"
        }
    
    Returns:
        dict: Fiche cocktail générée ou erreur
    """
    try:
        # Validation des données d'entrée
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'error': 'Le champ "prompt" est requis'
            }), 400
        
        user_prompt = data['prompt'].strip()
        if not user_prompt:
            return jsonify({
                'error': 'Le prompt ne peut pas être vide'
            }), 400
        
        logger.info(f"Génération d'un cocktail pour le prompt: {user_prompt[:100]}...")
        
        # Génération du cocktail via Mistral
        cocktail_data = mistral_service.generate_cocktail(user_prompt)
        
        if not cocktail_data:
            return jsonify({
                'error': 'Erreur lors de la génération du cocktail'
            }), 500
        
        # Sauvegarde en base de données
        cocktail = Cocktail(
            name=cocktail_data['name'],
            ingredients=cocktail_data['ingredients'],
            description=cocktail_data['description'],
            music_ambiance=cocktail_data['music_ambiance'],
            image_prompt=cocktail_data.get('image_prompt', ''),
            user_prompt=user_prompt
        )
        
        db.session.add(cocktail)
        db.session.commit()
        
        logger.info(f"Cocktail '{cocktail.name}' sauvegardé avec l'ID {cocktail.id}")
        
        return jsonify({
            'success': True,
            'cocktail': cocktail.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du cocktail: {str(e)}")
        return jsonify({
            'error': 'Erreur interne du serveur'
        }), 500

@app.route('/api/cocktails', methods=['GET'])
def get_cocktails():
    """
    Récupère la liste des cocktails générés (historique).
    
    Query parameters:
        - page: Numéro de page (défaut: 1)
        - per_page: Nombre d'éléments par page (défaut: 10, max: 50)
    
    Returns:
        dict: Liste paginée des cocktails
    """
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        # Récupération des cocktails avec pagination
        cocktails_query = Cocktail.query.order_by(Cocktail.created_at.desc())
        cocktails_paginated = cocktails_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        cocktails_list = [cocktail.to_dict() for cocktail in cocktails_paginated.items]
        
        return jsonify({
            'cocktails': cocktails_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': cocktails_paginated.total,
                'pages': cocktails_paginated.pages,
                'has_next': cocktails_paginated.has_next,
                'has_prev': cocktails_paginated.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cocktails: {str(e)}")
        return jsonify({
            'error': 'Erreur interne du serveur'
        }), 500

@app.route('/api/cocktails/<int:cocktail_id>', methods=['GET'])
def get_cocktail(cocktail_id):
    """
    Récupère un cocktail spécifique par son ID.
    
    Args:
        cocktail_id (int): ID du cocktail à récupérer
    
    Returns:
        JSON: Données du cocktail ou erreur 404
    """
    try:
        cocktail = Cocktail.query.get_or_404(cocktail_id)
        
        return jsonify({
            'success': True,
            'cocktail': cocktail.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du cocktail {cocktail_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération du cocktail'
        }), 500

@app.route('/api/cocktails/<int:cocktail_id>', methods=['DELETE'])
def delete_cocktail(cocktail_id):
    """
    Supprime un cocktail spécifique par son ID.
    
    Args:
        cocktail_id (int): ID du cocktail à supprimer
    
    Returns:
        JSON: Confirmation de suppression ou erreur
    """
    try:
        cocktail = Cocktail.query.get_or_404(cocktail_id)
        db.session.delete(cocktail)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cocktail supprimé avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du cocktail {cocktail_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la suppression du cocktail'
        }), 500

@app.route('/api/cocktails/generate-image', methods=['POST'])
def generate_image():
    """
    Génère une image pour un cocktail spécifique via DynaPictures.
    
    Expected JSON:
        {
            "cocktail_id": 123
        }
    
    Returns:
        JSON: URL de l'image générée ou erreur
    """
    try:
        # Validation des données d'entrée
        data = request.get_json()
        if not data or 'cocktail_id' not in data:
            return jsonify({
                'success': False,
                'error': 'L\'ID du cocktail est requis'
            }), 400
        
        cocktail_id = data['cocktail_id']
        if not isinstance(cocktail_id, int) or cocktail_id <= 0:
            return jsonify({
                'success': False,
                'error': 'L\'ID du cocktail doit être un entier positif'
            }), 400
        
        # Récupération du cocktail depuis la base de données
        cocktail = Cocktail.query.get(cocktail_id)
        if not cocktail:
            return jsonify({
                'success': False,
                'error': 'Cocktail non trouvé'
            }), 404
        
        logger.info(f"Génération d'image demandée pour le cocktail: {cocktail.name} (ID: {cocktail_id})")
        
        # Conversion du cocktail en dictionnaire pour le service
        cocktail_data = cocktail.to_dict()
        
        # Génération de l'image via DynaPictures
        image_url = mistral_service.generate_image(cocktail_data)
        
        if image_url:
            logger.info(f"Image générée avec succès pour {cocktail.name}: {image_url}")
            
            # Optionnel: Sauvegarder le chemin de l'image dans la base de données
            # pour éviter de régénérer à chaque fois
            if hasattr(cocktail, 'image_path'):
                cocktail.image_path = image_url
                db.session.commit()
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'cocktail_id': cocktail_id,
                'cocktail_name': cocktail.name
            })
        else:
            logger.warning(f"Génération d'image non disponible pour {cocktail.name}")
            return jsonify({
                'success': False,
                'error': 'Génération d\'images temporairement indisponible',
                'message': 'Le service DynaPictures n\'est pas configuré ou indisponible.'
            }), 503  # Service Unavailable
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'image: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@app.route('/<path:filename>')
def serve_static_files(filename):
    """
    Sert les fichiers statiques (images) depuis le répertoire frontend/public.
    
    Args:
        filename (str): Nom du fichier à servir
    
    Returns:
        File: Fichier statique ou erreur 404
    """
    try:
        # Chemin vers le répertoire public du frontend
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'public')
        return send_from_directory(static_dir, filename)
    except FileNotFoundError:
        return jsonify({
            'error': f'Fichier {filename} non trouvé'
        }), 404

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404."""
    return jsonify({
        'error': 'Endpoint non trouvé'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500."""
    return jsonify({
        'error': 'Erreur interne du serveur'
    }), 500

if __name__ == '__main__':
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
        logger.info("Base de données initialisée")
    
    # Démarrage du serveur de développement
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    )