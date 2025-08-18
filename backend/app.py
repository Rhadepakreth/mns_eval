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
from werkzeug.exceptions import BadRequest

# Import du module de sécurité
from security import (
    SecurityConfig, SecurityValidator, rate_limit, 
    add_security_headers, log_security_event, secure_error_handler
)

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging sécurisé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if os.getenv('LOG_TO_FILE') == 'true' else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration sécurisée de l'application
app.config['SECRET_KEY'] = SecurityConfig.get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = SecurityConfig.get_database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Configuration CORS sécurisée
cors_origins = SecurityConfig.get_cors_origins()
CORS(app, origins=cors_origins, supports_credentials=False)

# Initialisation de la base de données
db = SQLAlchemy(app)

# Import des modèles après initialisation de db
import models
Cocktail = models.create_models(db)

# Import des services
from services.mistral_service import MistralService

# Initialisation du service Mistral
mistral_service = MistralService()

# Middleware de sécurité
@app.after_request
def after_request(response):
    """Ajoute les headers de sécurité à toutes les réponses."""
    return add_security_headers(response)

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

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    Endpoint de vérification du statut des services.
    
    Returns:
        dict: Statut des services disponibles
    """
    try:
        # Vérifier la disponibilité du service d'image
        image_service_available = mistral_service.is_image_service_available()
        
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'mistral': True,  # Toujours disponible si l'app démarre
                'image_service_available': image_service_available,
                'image_service_type': mistral_service.get_image_service_type() if image_service_available else None
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/cocktails/generate', methods=['POST'])
@rate_limit(limit=5, window=60)  # 5 requêtes par minute
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
            log_security_event('INVALID_REQUEST', 'Champ prompt manquant')
            return jsonify({
                'error': 'Le champ "prompt" est requis'
            }), 400
        
        # Validation et sanitisation sécurisée du prompt
        try:
            user_prompt = SecurityValidator.sanitize_prompt(data['prompt'])
        except ValueError as e:
            log_security_event('INVALID_INPUT', f'Prompt invalide: {str(e)}')
            return jsonify({
                'error': str(e)
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
@rate_limit(limit=20, window=60)  # 20 requêtes par minute
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
        # Paramètres de pagination sécurisés
        page_param = request.args.get('page', 1)
        per_page_param = request.args.get('per_page', 10)
        page, per_page = SecurityValidator.validate_pagination_params(page_param, per_page_param)
        
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
@rate_limit(limit=30, window=60)  # 30 requêtes par minute
def get_cocktail(cocktail_id):
    """
    Récupère un cocktail spécifique par son ID.
    
    Args:
        cocktail_id (int): ID du cocktail à récupérer
    
    Returns:
        JSON: Données du cocktail ou erreur 404
    """
    try:
        # Validation sécurisée de l'ID
        try:
            cocktail_id = SecurityValidator.validate_cocktail_id(cocktail_id)
        except ValueError as e:
            log_security_event('INVALID_COCKTAIL_ID', f'ID invalide: {cocktail_id}')
            return jsonify({
                'error': str(e)
            }), 400
        
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
@rate_limit(limit=10, window=60)  # 10 suppressions par minute
def delete_cocktail(cocktail_id):
    """
    Supprime un cocktail spécifique par son ID et son image associée.
    
    Args:
        cocktail_id (int): ID du cocktail à supprimer
    
    Returns:
        JSON: Confirmation de suppression ou erreur
    """
    try:
        # Validation sécurisée de l'ID
        try:
            cocktail_id = SecurityValidator.validate_cocktail_id(cocktail_id)
        except ValueError as e:
            log_security_event('INVALID_COCKTAIL_ID', f'ID invalide pour suppression: {cocktail_id}')
            return jsonify({
                'error': str(e)
            }), 400
        
        cocktail = Cocktail.query.get_or_404(cocktail_id)
        
        # Suppression sécurisée de l'image associée si elle existe
        image_deleted = False
        if cocktail.image_path:
            try:
                # Validation du chemin pour éviter les attaques de traversée de répertoire
                if '..' in cocktail.image_path or not cocktail.image_path.strip():
                    log_security_event('PATH_TRAVERSAL_ATTEMPT', f'Tentative de traversée: {cocktail.image_path}')
                    logger.warning(f"⚠️ Chemin d'image invalide détecté: {cocktail.image_path}")
                else:
                    # Construire le chemin complet vers l'image
                    # Le chemin stocké est relatif (ex: "/cocktail_name.png")
                    # Le dossier public est dans frontend/public/
                    image_filename = cocktail.image_path.lstrip('/')
                    image_full_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'frontend', 'public', image_filename
                    )
                    
                    # Vérifier que le fichier existe et le supprimer
                    if os.path.exists(image_full_path):
                        os.remove(image_full_path)
                        image_deleted = True
                        logger.info(f"🗑️ Image supprimée: {image_full_path}")
                    else:
                        logger.warning(f"⚠️ Image non trouvée: {image_full_path}")
                    
            except Exception as img_error:
                logger.error(f"❌ Erreur lors de la suppression de l'image {cocktail.image_path}: {str(img_error)}")
                # On continue même si la suppression de l'image échoue
        
        # Supprimer le cocktail de la base de données
        cocktail_name = cocktail.name
        db.session.delete(cocktail)
        db.session.commit()
        
        message = f'Cocktail "{cocktail_name}" supprimé avec succès'
        if image_deleted:
            message += ' (image incluse)'
        elif cocktail.image_path:
            message += ' (image non trouvée)'
            
        logger.info(f"✅ {message}")
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du cocktail {cocktail_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la suppression du cocktail'
        }), 500

@app.route('/api/cocktails/generate-image', methods=['POST'])
@rate_limit(limit=3, window=60)  # 3 générations d'images par minute
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
            log_security_event('INVALID_REQUEST', 'ID cocktail manquant pour génération image')
            return jsonify({
                'success': False,
                'error': 'L\'ID du cocktail est requis'
            }), 400
        
        # Validation sécurisée de l'ID
        try:
            cocktail_id = SecurityValidator.validate_cocktail_id(data['cocktail_id'])
        except ValueError as e:
            log_security_event('INVALID_COCKTAIL_ID', f'ID invalide pour génération image: {data["cocktail_id"]}')
            return jsonify({
                'success': False,
                'error': str(e)
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
            
            # Sauvegarder le chemin de l'image dans la base de données
            try:
                cocktail.image_path = image_url
                db.session.commit()
                logger.info(f"Chemin d'image sauvegardé pour {cocktail.name}")
            except Exception as db_error:
                logger.warning(f"Erreur lors de la sauvegarde du chemin d'image: {db_error}")
                db.session.rollback()
                # Continue même si la sauvegarde échoue
            
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
@rate_limit(limit=50, window=60)  # 50 fichiers par minute
def serve_static_files(filename):
    """
    Sert les fichiers statiques (images) depuis le répertoire frontend/public.
    
    Args:
        filename (str): Nom du fichier à servir
    
    Returns:
        File: Fichier statique ou erreur 404
    """
    try:
        # Validation sécurisée du nom de fichier
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            log_security_event('PATH_TRAVERSAL_ATTEMPT', f'Tentative de traversée dans fichier statique: {filename}')
            return jsonify({
                'error': 'Nom de fichier invalide'
            }), 400
        
        # Vérification de l'extension de fichier autorisée
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'}
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            log_security_event('UNAUTHORIZED_FILE_ACCESS', f'Extension non autorisée: {filename}')
            return jsonify({
                'error': 'Type de fichier non autorisé'
            }), 403
        
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
    log_security_event('NOT_FOUND', f'Endpoint non trouvé: {request.path}')
    return secure_error_handler(404, 'Endpoint non trouvé')

@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500."""
    log_security_event('INTERNAL_ERROR', f'Erreur interne: {str(error)}')
    return secure_error_handler(500, 'Erreur interne du serveur')

@app.errorhandler(400)
def bad_request(error):
    """Gestionnaire d'erreur 400."""
    log_security_event('BAD_REQUEST', f'Requête invalide: {str(error)}')
    return secure_error_handler(400, 'Requête invalide')

@app.errorhandler(403)
def forbidden(error):
    """Gestionnaire d'erreur 403."""
    log_security_event('FORBIDDEN', f'Accès interdit: {request.path}')
    return secure_error_handler(403, 'Accès interdit')

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Gestionnaire d'erreur 429."""
    log_security_event('RATE_LIMIT_EXCEEDED', f'Limite de taux dépassée: {request.remote_addr}')
    return secure_error_handler(429, 'Trop de requêtes')

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