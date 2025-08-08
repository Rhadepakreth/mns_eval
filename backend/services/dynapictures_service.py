#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de génération d'images avec Stable Diffusion pour Le Mixologue Augmenté

Gère la génération d'images de cocktails en utilisant des modèles Stable Diffusion
avancés (SDXL, SD 2.1, SD 1.5) avec authentification Hugging Face.
Supporte la sélection automatique du meilleur modèle selon les ressources disponibles.

Auteur: Assistant IA
Date: 2024
"""

import os
import logging
import torch
from typing import Dict, Optional, Any, Tuple
from datetime import datetime
from diffusers import (
    DiffusionPipeline, 
    StableDiffusionXLPipeline,
    StableDiffusionPipeline,
    EulerDiscreteScheduler
)
from huggingface_hub import login
from PIL import Image
import re

logger = logging.getLogger(__name__)

class DynaPicturesService:
    """
    Service de génération d'images avec Stable Diffusion avancé.
    
    Supporte plusieurs modèles Stable Diffusion (SDXL, SD 2.1, SD 1.5) avec
    sélection automatique du meilleur modèle selon les ressources disponibles.
    Optimise automatiquement les paramètres selon le modèle choisi.
    """
    
    # Configuration des modèles disponibles
    MODELS_CONFIG = {
        "sdxl": {
            "id": "stabilityai/stable-diffusion-xl-base-1.0",
            "pipeline_class": StableDiffusionXLPipeline,
            "resolution": (1024, 1024),
            "min_vram_gb": 10,
            "steps": 25,
            "guidance_scale": 7.5,
            "description": "SDXL 1.0 - Qualité supérieure, résolution 1024x1024"
        },
        "sd21": {
            "id": "stabilityai/stable-diffusion-2-1",
            "pipeline_class": StableDiffusionPipeline,
            "resolution": (768, 768),
            "min_vram_gb": 6,
            "steps": 20,
            "guidance_scale": 7.5,
            "description": "SD 2.1 - Bon équilibre qualité/performance, résolution 768x768"
        },
        "sd15": {
            "id": "runwayml/stable-diffusion-v1-5",
            "pipeline_class": StableDiffusionPipeline,
            "resolution": (512, 512),
            "min_vram_gb": 4,
            "steps": 15,
            "guidance_scale": 7.0,
            "description": "SD 1.5 - Rapide et compatible, résolution 512x512"
        }
    }
    
    def __init__(self, preferred_model: str = "auto"):
        """
        Initialise le service Stable Diffusion avec sélection automatique du modèle.
        
        Args:
            preferred_model: Modèle préféré ("sdxl", "sd21", "sd15", "auto")
                           "auto" sélectionne automatiquement selon les ressources
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
        self.current_model = None
        self.model_config = None
        
        # Sélection du modèle optimal
        self.selected_model = self._select_optimal_model(preferred_model)
        self.model_config = self.MODELS_CONFIG[self.selected_model]
        logger.info(f"🎯 Modèle sélectionné: {self.selected_model} - {self.model_config['description']}")
        
        # Authentification Hugging Face
        try:
            login(token=self.hf_token)
            logger.info("✅ Connexion réussie à Hugging Face !")
        except Exception as e:
            logger.error(f"❌ Erreur d'authentification Hugging Face: {e}")
            raise ValueError(f"Authentification Hugging Face échouée: {e}")
        
        # Initialisation du pipeline (lazy loading)
        self._initialize_pipeline()
    
    def _select_optimal_model(self, preferred_model: str) -> str:
        """
        Sélectionne le modèle optimal selon les ressources disponibles.
        
        Args:
            preferred_model: Modèle préféré ou "auto" pour sélection automatique
            
        Returns:
            str: Clé du modèle sélectionné
        """
        if preferred_model != "auto" and preferred_model in self.MODELS_CONFIG:
            logger.info(f"🎯 Utilisation du modèle spécifié: {preferred_model}")
            return preferred_model
        
        # Sélection automatique basée sur les ressources
        available_vram = self._get_available_vram()
        logger.info(f"💾 VRAM disponible estimée: {available_vram:.1f} GB")
        
        # Ordre de préférence: SDXL > SD2.1 > SD1.5
        for model_key in ["sdxl", "sd21", "sd15"]:
            model_config = self.MODELS_CONFIG[model_key]
            if available_vram >= model_config["min_vram_gb"]:
                logger.info(f"✅ Modèle {model_key} compatible avec {available_vram:.1f} GB VRAM")
                return model_key
        
        # Fallback sur SD1.5 si aucun modèle n'est compatible
        logger.warning("⚠️ VRAM insuffisante, utilisation de SD1.5 par défaut")
        return "sd15"
    
    def _get_available_vram(self) -> float:
        """
        Estime la VRAM disponible.
        
        Returns:
            float: VRAM disponible en GB
        """
        if not torch.cuda.is_available():
            return 0.0
        
        try:
            # Obtenir la VRAM totale et utilisée
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            available_memory = total_memory - allocated_memory
            
            # Conversion en GB avec marge de sécurité (80% de la VRAM disponible)
            available_gb = (available_memory / (1024**3)) * 0.8
            
            return max(0.0, available_gb)
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'estimer la VRAM: {e}")
            # Estimation conservative pour CPU ou erreur
            return 4.0 if self.device == "cuda" else 0.0
    
    def _initialize_pipeline(self):
        """
        Initialise le pipeline Stable Diffusion selon le modèle sélectionné.
        
        Utilise le lazy loading pour éviter de charger le modèle si non nécessaire.
        Configure automatiquement le device et les optimisations selon le modèle.
        """
        try:
            model_id = self.model_config["id"]
            pipeline_class = self.model_config["pipeline_class"]
            
            logger.info(f"🔄 Initialisation du pipeline {self.selected_model} ({model_id}) sur {self.device}...")
            
            # Configuration optimisée selon le device et le modèle
            if self.device == "cuda":
                # Configuration CUDA avec optimisations
                self.pipe = pipeline_class.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16" if self.selected_model == "sdxl" else None
                ).to(self.device)
                
                # Optimisations spécifiques selon le modèle
                if self.selected_model == "sdxl":
                    # SDXL nécessite plus de VRAM, optimisations agressives
                    self.pipe.enable_model_cpu_offload()
                    self.pipe.enable_attention_slicing()
                    # Scheduler optimisé pour SDXL
                    self.pipe.scheduler = EulerDiscreteScheduler.from_config(
                        self.pipe.scheduler.config
                    )
                else:
                    # SD 2.1 et 1.5 - optimisations standard
                    self.pipe.enable_attention_slicing()
                    if self.selected_model == "sd21":
                        self.pipe.enable_model_cpu_offload()
                
            else:
                logger.warning("⚠️ CUDA non disponible, utilisation du CPU (plus lent)")
                self.pipe = pipeline_class.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32
                ).to(self.device)
            
            self.current_model = self.selected_model
            logger.info(f"✅ Pipeline {self.selected_model} initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation du pipeline {self.selected_model}: {e}")
            # Fallback vers SD1.5 en cas d'erreur
            if self.selected_model != "sd15":
                logger.info("🔄 Tentative de fallback vers SD1.5...")
                self._fallback_to_sd15()
            else:
                raise RuntimeError(f"Impossible d'initialiser Stable Diffusion: {e}")
    
    def _fallback_to_sd15(self):
        """
        Fallback vers SD1.5 en cas d'échec du modèle principal.
        """
        try:
            self.selected_model = "sd15"
            self.model_config = self.MODELS_CONFIG["sd15"]
            
            logger.info("🔄 Initialisation du fallback SD1.5...")
            
            if self.device == "cuda":
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_config["id"],
                    torch_dtype=torch.float16,
                    use_safetensors=True
                ).to(self.device)
                self.pipe.enable_attention_slicing()
            else:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_config["id"],
                    torch_dtype=torch.float32
                ).to(self.device)
            
            self.current_model = "sd15"
            logger.info("✅ Fallback SD1.5 initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Échec du fallback SD1.5: {e}")
            raise RuntimeError(f"Impossible d'initialiser le fallback SD1.5: {e}")
    
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
    
    def _get_negative_prompt(self) -> str:
        """
        Retourne le prompt négatif optimisé selon le modèle utilisé.
        
        Returns:
            str: Prompt négatif adapté au modèle
        """
        base_negative = "blurry, low quality, distorted, ugly, bad anatomy"
        
        if self.current_model == "sdxl":
            # SDXL bénéficie de prompts négatifs plus détaillés
            return f"{base_negative}, worst quality, low resolution, jpeg artifacts, watermark, signature, text, logo"
        elif self.current_model == "sd21":
            # SD 2.1 avec prompts négatifs modérés
            return f"{base_negative}, worst quality, low resolution, jpeg artifacts"
        else:
            # SD 1.5 avec prompts négatifs simples
            return base_negative
    
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
        Génère une image de cocktail en utilisant le modèle Stable Diffusion sélectionné.
        
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
            logger.info(f"📊 Modèle utilisé: {self.current_model} - {self.model_config['description']}")
            
            # Construction du prompt optimisé
            prompt = self._build_cocktail_prompt(cocktail_data)
            
            # Génération de l'image
            logger.info(f"🔄 Génération en cours avec {self.current_model}...")
            
            # Paramètres optimisés selon le modèle
            width, height = self.model_config["resolution"]
            generation_params = {
                "prompt": prompt,
                "num_inference_steps": self.model_config["steps"],
                "guidance_scale": self.model_config["guidance_scale"],
                "width": width,
                "height": height,
                "negative_prompt": self._get_negative_prompt(),
                "num_images_per_prompt": 1
            }
            
            # Paramètres spécifiques pour SDXL
            if self.current_model == "sdxl":
                generation_params.update({
                    "denoising_end": 0.8,  # Utilise le refiner implicitement
                    "output_type": "pil"
                })
            
            logger.info(f"⚙️ Paramètres: {width}x{height}, {self.model_config['steps']} étapes, guidance {self.model_config['guidance_scale']}")
            
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