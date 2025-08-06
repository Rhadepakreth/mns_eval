#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèles de données pour Le Mixologue Augmenté

Définit les structures de données pour la base SQLite.
Utilise SQLAlchemy ORM pour la gestion des données.

Auteur: Assistant IA
Date: 2024
"""

from datetime import datetime
import json

def create_models(db):
    """
    Crée les modèles avec l'instance de base de données fournie.
    Cette approche évite les imports circulaires.
    """
    
    class Cocktail(db.Model):
        """
        Modèle représentant un cocktail généré par l'IA.
        
        Stocke toutes les informations d'une fiche cocktail :
        - Nom créatif du cocktail
        - Liste des ingrédients avec quantités
        - Description/histoire du cocktail
        - Suggestion d'ambiance musicale
        - Prompt image optionnel pour génération d'image
        - Prompt utilisateur original
        """
        
        __tablename__ = 'cocktails'
        
        # Clé primaire
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        
        # Informations du cocktail
        name = db.Column(db.String(200), nullable=False, index=True,
                        comment="Nom créatif du cocktail généré par l'IA")
        
        ingredients = db.Column(db.Text, nullable=False,
                               comment="Liste des ingrédients au format JSON")
        
        description = db.Column(db.Text, nullable=False,
                               comment="Histoire/description courte du cocktail")
        
        music_ambiance = db.Column(db.Text, nullable=False,
                                  comment="Suggestion d'ambiance musicale")
        
        image_prompt = db.Column(db.Text, nullable=True,
                                comment="Prompt pour génération d'image (optionnel)")
        
        # Métadonnées
        user_prompt = db.Column(db.Text, nullable=False,
                               comment="Demande originale de l'utilisateur")
        
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                              index=True, comment="Date de création du cocktail")
        
        updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                              onupdate=datetime.utcnow,
                              comment="Date de dernière modification")
        
        def __init__(self, name, ingredients, description, music_ambiance, 
                     user_prompt, image_prompt=None):
            """
            Initialise un nouveau cocktail.
            
            Args:
                name (str): Nom du cocktail
                ingredients (str|list): Ingrédients (JSON string ou liste)
                description (str): Description du cocktail
                music_ambiance (str): Ambiance musicale
                user_prompt (str): Demande utilisateur originale
                image_prompt (str, optional): Prompt pour image
            """
            self.name = name
            self.ingredients = self._serialize_ingredients(ingredients)
            self.description = description
            self.music_ambiance = music_ambiance
            self.user_prompt = user_prompt
            self.image_prompt = image_prompt or ''
        
        def _serialize_ingredients(self, ingredients):
            """
            Sérialise les ingrédients en JSON si nécessaire.
            
            Args:
                ingredients (str|list|dict): Ingrédients à sérialiser
            
            Returns:
                str: JSON string des ingrédients
            """
            if isinstance(ingredients, str):
                # Vérifie si c'est déjà du JSON valide
                try:
                    json.loads(ingredients)
                    return ingredients
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON, on l'encapsule
                    return json.dumps([ingredients])
            
            # Si c'est une liste ou un dict, on sérialise
            return json.dumps(ingredients, ensure_ascii=False)
        
        def get_ingredients_list(self):
            """
            Retourne les ingrédients sous forme de liste Python.
            
            Returns:
                list: Liste des ingrédients
            """
            try:
                return json.loads(self.ingredients)
            except json.JSONDecodeError:
                # Fallback si le JSON est corrompu
                return [self.ingredients]
        
        def to_dict(self):
            """
            Convertit le cocktail en dictionnaire pour sérialisation JSON.
            
            Returns:
                dict: Représentation dictionnaire du cocktail
            """
            return {
                'id': self.id,
                'name': self.name,
                'ingredients': self.get_ingredients_list(),
                'description': self.description,
                'music_ambiance': self.music_ambiance,
                'image_prompt': self.image_prompt,
                'user_prompt': self.user_prompt,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        
        def __repr__(self):
            """
            Représentation string du cocktail pour le debugging.
            
            Returns:
                str: Représentation du cocktail
            """
            return f'<Cocktail {self.id}: "{self.name}">'
        
        def __str__(self):
            """
            Représentation string lisible du cocktail.
            
            Returns:
                str: Nom du cocktail
            """
            return self.name
        
        @classmethod
        def search_by_name(cls, search_term):
            """
            Recherche des cocktails par nom (recherche partielle).
            
            Args:
                search_term (str): Terme de recherche
            
            Returns:
                Query: Query SQLAlchemy pour les cocktails trouvés
            """
            return cls.query.filter(
                cls.name.ilike(f'%{search_term}%')
            ).order_by(cls.created_at.desc())
        
        @classmethod
        def search_by_ingredients(cls, ingredient_term):
            """
            Recherche des cocktails par ingrédients.
            
            Args:
                ingredient_term (str): Terme de recherche dans les ingrédients
            
            Returns:
                Query: Query SQLAlchemy pour les cocktails trouvés
            """
            return cls.query.filter(
                cls.ingredients.ilike(f'%{ingredient_term}%')
            ).order_by(cls.created_at.desc())
        
        @classmethod
        def get_recent(cls, limit=10):
            """
            Récupère les cocktails les plus récents.
            
            Args:
                limit (int): Nombre maximum de cocktails à retourner
            
            Returns:
                list: Liste des cocktails récents
            """
            return cls.query.order_by(
                cls.created_at.desc()
            ).limit(limit).all()
        
        @classmethod
        def get_stats(cls):
            """
            Retourne des statistiques sur les cocktails.
            
            Returns:
                dict: Statistiques (nombre total, date du premier/dernier)
            """
            total = cls.query.count()
            
            if total == 0:
                return {
                    'total': 0,
                    'first_created': None,
                    'last_created': None
                }
            
            first = cls.query.order_by(cls.created_at.asc()).first()
            last = cls.query.order_by(cls.created_at.desc()).first()
            
            return {
                'total': total,
                'first_created': first.created_at.isoformat() if first else None,
                'last_created': last.created_at.isoformat() if last else None
            }
    
    return Cocktail