#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de sécurité pour Le Mixologue Augmenté

Centralise toutes les mesures de sécurité de l'application :
- Validation et sanitisation des entrées
- Headers de sécurité
- Rate limiting
- Gestion sécurisée des erreurs
- Configuration sécurisée

Auteur: Assistant IA
Date: 2024
"""

import os
import re
import secrets
import hashlib
import logging
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
from flask import request, jsonify, g
from werkzeug.exceptions import BadRequest
from html import escape
import bleach

logger = logging.getLogger(__name__)

class SecurityConfig:
    """
    Configuration de sécurité centralisée.
    """
    
    # Génération d'une clé secrète sécurisée si non définie
    @staticmethod
    def get_secret_key():
        """Génère ou récupère une clé secrète sécurisée."""
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'dev-secret-key-change-in-production':
            # Génération d'une clé sécurisée de 32 bytes
            secret_key = secrets.token_hex(32)
            logger.warning("⚠️ Clé secrète générée automatiquement. Définissez SECRET_KEY en production.")
        return secret_key
    
    # Configuration CORS sécurisée
    @staticmethod
    def get_cors_origins():
        """Récupère les origines CORS autorisées de manière sécurisée."""
        cors_origins = os.getenv('CORS_ORIGINS', '')
        if not cors_origins:
            # Valeurs par défaut sécurisées pour le développement
            return ['http://localhost:5173', 'http://localhost:3000']
        
        # Validation des origines CORS
        origins = []
        for origin in cors_origins.split(','):
            origin = origin.strip()
            if SecurityValidator.is_valid_url(origin):
                origins.append(origin)
            else:
                logger.warning(f"⚠️ Origine CORS invalide ignorée: {origin}")
        
        return origins if origins else ['http://localhost:5173']
    
    # Configuration de base de données sécurisée
    @staticmethod
    def get_database_url():
        """Récupère l'URL de base de données de manière sécurisée."""
        db_url = os.getenv('DATABASE_URL', 'sqlite:///cocktails.db')
        
        # Validation basique de l'URL de base de données
        if not db_url.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
            logger.error("❌ URL de base de données invalide")
            raise ValueError("URL de base de données invalide")
        
        return db_url

class SecurityValidator:
    """
    Validateur et sanitiseur d'entrées utilisateur.
    """
    
    # Patterns de validation
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domaine
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # TLD
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port optionnel
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    PROMPT_PATTERN = re.compile(r'^[\w\s\-.,!?àâäéèêëïîôöùûüÿç]+$', re.UNICODE)
    
    @staticmethod
    def is_valid_url(url):
        """Valide une URL."""
        if not url or len(url) > 2048:
            return False
        return bool(SecurityValidator.URL_PATTERN.match(url))
    
    @staticmethod
    def sanitize_prompt(prompt):
        """
        Sanitise et valide un prompt utilisateur.
        
        Args:
            prompt (str): Prompt à sanitiser
        
        Returns:
            str: Prompt sanitisé
        
        Raises:
            ValueError: Si le prompt est invalide
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Le prompt doit être une chaîne non vide")
        
        # Suppression des espaces en début/fin
        prompt = prompt.strip()
        
        # Vérification de la longueur
        if len(prompt) < 3:
            raise ValueError("Le prompt doit contenir au moins 3 caractères")
        if len(prompt) > 1000:
            raise ValueError("Le prompt ne peut pas dépasser 1000 caractères")
        
        # Échappement HTML pour prévenir XSS
        prompt = escape(prompt)
        
        # Nettoyage avec bleach pour supprimer tout HTML/script
        prompt = bleach.clean(prompt, tags=[], strip=True)
        
        # Validation du contenu (caractères autorisés)
        if not SecurityValidator.PROMPT_PATTERN.match(prompt):
            raise ValueError("Le prompt contient des caractères non autorisés")
        
        return prompt
    
    @staticmethod
    def validate_cocktail_id(cocktail_id):
        """
        Valide un ID de cocktail.
        
        Args:
            cocktail_id: ID à valider
        
        Returns:
            int: ID validé
        
        Raises:
            ValueError: Si l'ID est invalide
        """
        try:
            cocktail_id = int(cocktail_id)
            if cocktail_id <= 0:
                raise ValueError("L'ID doit être un entier positif")
            if cocktail_id > 2147483647:  # Limite INT32
                raise ValueError("L'ID est trop grand")
            return cocktail_id
        except (TypeError, ValueError) as e:
            raise ValueError(f"ID de cocktail invalide: {e}")
    
    @staticmethod
    def validate_pagination_params(page, per_page):
        """
        Valide les paramètres de pagination.
        
        Args:
            page: Numéro de page
            per_page: Éléments par page
        
        Returns:
            tuple: (page, per_page) validés
        """
        try:
            page = max(1, int(page or 1))
            per_page = max(1, min(50, int(per_page or 10)))  # Limite à 50
            return page, per_page
        except (TypeError, ValueError):
            return 1, 10

class RateLimiter:
    """
    Système de limitation de taux simple en mémoire.
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = defaultdict(datetime)
    
    def is_allowed(self, ip_address, endpoint, limit=10, window=60):
        """
        Vérifie si une requête est autorisée selon le rate limiting.
        
        Args:
            ip_address (str): Adresse IP du client
            endpoint (str): Endpoint appelé
            limit (int): Nombre max de requêtes
            window (int): Fenêtre de temps en secondes
        
        Returns:
            bool: True si autorisé, False sinon
        """
        now = datetime.now()
        key = f"{ip_address}:{endpoint}"
        
        # Vérifier si l'IP est temporairement bloquée
        if key in self.blocked_ips:
            if now < self.blocked_ips[key]:
                return False
            else:
                del self.blocked_ips[key]
        
        # Nettoyer les anciennes requêtes
        cutoff = now - timedelta(seconds=window)
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Vérifier la limite
        if len(self.requests[key]) >= limit:
            # Bloquer l'IP pour 5 minutes
            self.blocked_ips[key] = now + timedelta(minutes=5)
            logger.warning(f"🚫 Rate limit dépassé pour {ip_address} sur {endpoint}")
            return False
        
        # Enregistrer la requête
        self.requests[key].append(now)
        return True

# Instance globale du rate limiter
rate_limiter = RateLimiter()

def rate_limit(limit=10, window=60, per_endpoint=True):
    """
    Décorateur pour appliquer le rate limiting.
    
    Args:
        limit (int): Nombre max de requêtes
        window (int): Fenêtre de temps en secondes
        per_endpoint (bool): Appliquer par endpoint ou globalement
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if not ip_address:
                ip_address = '127.0.0.1'
            
            endpoint = request.endpoint if per_endpoint else 'global'
            
            if not rate_limiter.is_allowed(ip_address, endpoint, limit, window):
                return jsonify({
                    'error': 'Trop de requêtes. Veuillez patienter avant de réessayer.',
                    'retry_after': 300  # 5 minutes
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def add_security_headers(response):
    """
    Ajoute les headers de sécurité à toutes les réponses.
    
    Args:
        response: Objet Response Flask
    
    Returns:
        Response: Réponse avec headers de sécurité
    """
    # Protection XSS
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "media-src 'self'; "
        "frame-src 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # HSTS (uniquement en HTTPS)
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Référer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

def log_security_event(event_type, details, ip_address=None):
    """
    Enregistre un événement de sécurité.
    
    Args:
        event_type (str): Type d'événement
        details (str): Détails de l'événement
        ip_address (str): Adresse IP (optionnel)
    """
    ip = ip_address or request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    logger.warning(f"🔒 SÉCURITÉ [{event_type}] {details} - IP: {ip}")

def secure_error_handler(error):
    """
    Gestionnaire d'erreur sécurisé qui ne révèle pas d'informations sensibles.
    
    Args:
        error: Exception capturée
    
    Returns:
        tuple: (response, status_code)
    """
    # Log l'erreur complète pour le debugging
    logger.error(f"Erreur application: {str(error)}", exc_info=True)
    
    # Retourner une réponse générique à l'utilisateur
    return jsonify({
        'error': 'Une erreur interne s\'est produite',
        'timestamp': datetime.utcnow().isoformat()
    }), 500