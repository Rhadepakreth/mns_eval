#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de génération d'images avec Stable Diffusion pour Le Mixologue Augmenté

Gère la génération d'images de cocktails en utilisant Stable Diffusion v1.5
avec authentification Hugging Face. Remplace l'ancien service DynaPictures.

Auteur: Assistant IA
Date: 2024
"""

import os
import logging
import torch
from typing import Dict, Optional, Any
from datetime import datetime
from diffusers import DiffusionPipeline
from huggingface_hub import login
from PIL import Image
import re

logger = logging.getLogger(__name__)

class DynaPicturesService:
    """
    Service de génération d'images avec Stable Diffusion v1.5.
    
    Utilise le modèle Stable Diffusion v1.5 de RunwayML pour générer
    des images de cocktails basées sur les descriptions et prompts fournis.
    Nécessite une authentification Hugging Face valide.
    """
    
    def __init__(self):
        """
        Initialise le service Stable Diffusion avec authentification Hugging Face.
        
        """
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if not self.hf_token or self.hf_token == '<VOTRE-TOKEN-HUGGINGFACE>':
            raise ValueError(
                "HUGGINGFACE_TOKEN non configuré. "
                "Veuillez définir cette variable d'environnement avec votre token Hugging Face. "
                "Générez un token sur https://huggingface.co/settings/tokens"
            )
        
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Utilisation d'un modèle accessible sans restriction
        self.model_id = "runwayml/stable-diffusion-v1-5"
        
        # Authentification Hugging Face
        try:
            login(token=self.hf_token)
            logger.info("✅ Connexion réussie à Hugging Face !")
        except Exception as e:
            logger.error(f"❌ Erreur d'authentification Hugging Face: {e}")
            raise ValueError(f"Authentification Hugging Face échouée: {e}")
        
        # Initialisation du pipeline (lazy loading)
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """
        Initialise le pipeline Stable Diffusion 3.5 Large.
        
        Utilise le lazy loading pour éviter de charger le modèle si non nécessaire.
        Configure automatiquement le device (CUDA si disponible, sinon CPU).
        """
        try:
            logger.info(f"🔄 Initialisation du pipeline Stable Diffusion v1.5 sur {self.device}...")
            
            # Configuration optimisée selon le device
            if self.device == "cuda":
                self.pipe = DiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True
                ).to(self.device)
                
                # Optimisations CUDA
                self.pipe.enable_model_cpu_offload()
                self.pipe.enable_attention_slicing()
            else:
                logger.warning("⚠️ CUDA non disponible, utilisation du CPU (plus lent)")
                self.pipe = DiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float32
                ).to(self.device)
            
            logger.info("✅ Pipeline Stable Diffusion initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation du pipeline: {e}")
            raise RuntimeError(f"Impossible d'initialiser Stable Diffusion: {e}")
    
    def _build_cocktail_prompt(self, cocktail_data: Dict[str, Any]) -> str:
        """
        Construit un prompt optimisé pour la génération d'image de cocktail.
        
        Args:
            cocktail_data: Données du cocktail contenant nom, ingrédients, description
        
        Returns:
            str: Prompt optimisé pour Stable Diffusion
        """
        cocktail_name = cocktail_data.get('name', 'Cocktail')
        ingredients = cocktail_data.get('ingredients', [])
        description = cocktail_data.get('description', '')
        image_prompt = cocktail_data.get('image_prompt', '')
        
        # Construction d'un prompt court et optimisé (ignorer l'image_prompt long)
        color_hints = self._extract_color_hints(ingredients, description)
        style_hints = self._extract_style_hints(cocktail_name, description)
        
        # Prompt de base très concis
        base_prompt = f"Beautiful {cocktail_name} cocktail, elegant glass, {color_hints}, {style_hints}"
        
        # Limitation stricte à 40 mots pour éviter complètement la troncature CLIP
        words = base_prompt.split()
        if len(words) > 35:  # Garde de la place pour les qualificatifs finaux
            base_prompt = ' '.join(words[:35])
        
        # Ajout de qualificatifs très courts
        enhanced_prompt = f"{base_prompt}, high quality, professional"
        
        # Vérification finale - maximum 40 mots
        final_words = enhanced_prompt.split()
        if len(final_words) > 40:
            enhanced_prompt = ' '.join(final_words[:40])
        
        logger.info(f"🎨 Prompt généré ({len(enhanced_prompt.split())} mots): {enhanced_prompt[:100]}...")
        return enhanced_prompt
    
    def _extract_color_hints(self, ingredients: list, description: str) -> str:
        """
        Extrait des indices de couleur basés sur les ingrédients et la description.
        
        Args:
            ingredients: Liste des ingrédients du cocktail
            description: Description textuelle du cocktail
        
        Returns:
            str: Indices de couleur pour le prompt
        """
        color_map = {
            'rhum': 'golden amber',
            'whisky': 'deep amber',
            'vodka': 'crystal clear',
            'gin': 'clear with botanical hints',
            'tequila': 'pale gold',
            'grenadine': 'ruby red gradient',
            'blue': 'vibrant blue',
            'rouge': 'deep red',
            'vert': 'emerald green',
            'citron': 'bright yellow',
            'orange': 'sunset orange',
            'cranberry': 'deep crimson',
            'passion': 'tropical orange'
        }
        
        colors = []
        text_to_analyze = ' '.join(ingredients).lower() + ' ' + description.lower()
        
        for ingredient, color in color_map.items():
            if ingredient in text_to_analyze:
                colors.append(color)
        
        if colors:
            return f"with {', '.join(colors[:2])} tones"
        return "with elegant color palette"
    
    def _extract_style_hints(self, name: str, description: str) -> str:
        """
        Extrait des indices de style basés sur le nom et la description.
        
        Args:
            name: Nom du cocktail
            description: Description du cocktail
        
        Returns:
            str: Indices de style pour le prompt
        """
        style_keywords = {
            'tropical': 'tropical paradise setting with palm leaves',
            'summer': 'bright summer atmosphere',
            'winter': 'cozy winter ambiance',
            'elegant': 'sophisticated upscale bar',
            'vintage': 'classic vintage style',
            'modern': 'contemporary minimalist design',
            'exotic': 'exotic luxurious presentation',
            'classic': 'timeless classic cocktail style'
        }
        
        text_to_analyze = (name + ' ' + description).lower()
        
        for keyword, style in style_keywords.items():
            if keyword in text_to_analyze:
                return style
        
        return "elegant bar atmosphere"
    
    def _sanitize_filename(self, cocktail_name: str) -> str:
        """
        Nettoie le nom du cocktail pour créer un nom de fichier valide.
        
        Args:
            cocktail_name: Nom original du cocktail
        
        Returns:
            str: Nom de fichier sécurisé
        """
        # Remplacer les caractères spéciaux et espaces
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', cocktail_name)
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        clean_name = clean_name.lower()
        
        # Limiter la longueur
        if len(clean_name) > 30:
            clean_name = clean_name[:30]
        
        return clean_name or 'cocktail'
    
    def generate_cocktail_image(self, cocktail_data: Dict[str, Any]) -> Optional[str]:
        """
        Génère une image de cocktail en utilisant Stable Diffusion 3.5 Large.
        
        Args:
            cocktail_data: Dictionnaire contenant les données du cocktail
                          (name, ingredients, description, image_prompt)
        
        Returns:
            Optional[str]: Chemin relatif vers l'image générée, ou None en cas d'erreur
        """
        try:
            # Vérification de l'état du pipeline
            if not self.pipe:
                logger.error("❌ Pipeline Stable Diffusion non initialisé")
                return None
                
            # Vérification que le pipeline est sur le bon device
            if hasattr(self.pipe, 'device') and self.pipe.device != self.device:
                logger.warning(f"⚠️ Pipeline sur device {self.pipe.device}, attendu {self.device}")
            
            cocktail_name = cocktail_data.get('name', 'Cocktail Inconnu')
            logger.info(f"🎨 Génération d'image pour le cocktail: {cocktail_name}")
            
            # Construction du prompt optimisé
            prompt = self._build_cocktail_prompt(cocktail_data)
            
            # Génération de l'image
            logger.info("🔄 Génération en cours avec Stable Diffusion 3.5 Large...")
            
            # Paramètres ultra-conservateurs pour éviter les erreurs
            generation_params = {
                "prompt": prompt,
                "num_inference_steps": 15,  # Encore plus réduit
                "guidance_scale": 7.0,      # Valeur standard
                "width": 512,
                "height": 512,
                "negative_prompt": "blurry, low quality, distorted",  # Améliore la qualité
                "num_images_per_prompt": 1  # Explicitement une seule image
            }
            
            # Pas de generator pour éviter les erreurs d'index
            # Le modèle utilisera sa propre graine aléatoire
            
            # Génération avec gestion d'erreur robuste
            result = self.pipe(**generation_params)
            
            # Vérification que le résultat contient des images
            if not hasattr(result, 'images') or not result.images:
                logger.error("❌ Aucune image générée par le pipeline")
                return None
                
            image = result.images[0]
            
            # Vérification que l'image est valide
            if image is None:
                logger.error("❌ Image générée est None")
                return None
            
            # Sauvegarde de l'image
            filename = self._save_image(image, cocktail_name)
            if filename:
                logger.info(f"✅ Image générée et sauvegardée: {filename}")
                return filename
            else:
                logger.error("❌ Erreur lors de la sauvegarde de l'image")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération d'image: {e}")
            return None
    
    def _save_image(self, image: Image.Image, cocktail_name: str) -> Optional[str]:
        """
        Sauvegarde l'image générée dans le dossier public du frontend.
        
        Args:
            image: Image PIL générée
            cocktail_name: Nom du cocktail pour le nom de fichier
        
        Returns:
            Optional[str]: Chemin relatif vers l'image sauvegardée
        """
        try:
            # Création du nom de fichier unique
            clean_name = self._sanitize_filename(cocktail_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cocktail_{clean_name}_{timestamp}.png"
            
            # Chemin vers le dossier public du frontend
            frontend_public_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'frontend', 'public'
            )
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(frontend_public_dir, exist_ok=True)
            
            # Chemin complet du fichier
            file_path = os.path.join(frontend_public_dir, filename)
            
            # Sauvegarde avec optimisation
            image.save(file_path, "PNG", optimize=True, quality=95)
            
            # Retourner le chemin relatif pour l'URL
            relative_path = f"/{filename}"
            logger.info(f"💾 Image sauvegardée: {file_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Teste la connexion et la fonctionnalité du service Stable Diffusion.
        
        Returns:
            bool: True si le service fonctionne correctement
        """
        try:
            logger.info("🧪 Test de connexion Stable Diffusion...")
            
            if not self.pipe:
                logger.error("❌ Pipeline non initialisé")
                return False
            
            # Test avec un prompt simple
            test_prompt = "A simple elegant cocktail glass, professional photography"
            
            # Génération de test avec paramètres réduits pour la rapidité
            result = self.pipe(
                prompt=test_prompt,
                num_inference_steps=10,  # Réduit pour le test
                guidance_scale=7.5,
                width=512,               # Résolution réduite pour le test
                height=512
            )
            
            if result and result.images and len(result.images) > 0:
                logger.info("✅ Test de génération Stable Diffusion réussi")
                return True
            else:
                logger.error("❌ Test de génération échoué: aucune image générée")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test de connexion échoué: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le service de génération d'images.
        
        Returns:
            Dict[str, Any]: Informations sur le service
        """
        return {
            "service_name": "Stable Diffusion 3.5 Large",
            "model_id": self.model_id,
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "pipeline_loaded": self.pipe is not None,
            "hf_authenticated": bool(self.hf_token and self.hf_token != '<VOTRE-TOKEN-HUGGINGFACE>')
        }