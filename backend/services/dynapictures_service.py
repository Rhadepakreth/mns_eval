#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de génération d'images avec Stable Diffusion (DynaPictures)
Version simplifiée utilisant les prompts générés par Mistral
"""

import os
import torch
import logging
from datetime import datetime
from typing import Optional
from diffusers import DiffusionPipeline, DDIMScheduler
import PIL.Image

logger = logging.getLogger(__name__)

class DynaPicturesService:
    """
    Service simplifié de génération d'images avec Stable Diffusion.
    Utilise les prompts fournis par Mistral pour générer des images de cocktails.
    """
    
    def __init__(self):
        """
        Initialise le service avec le pipeline Stable Diffusion.
        """
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public')
        
        os.makedirs(self.output_dir, exist_ok=True)
        self._load_pipeline()

    def _load_pipeline(self):
        """
        Charge le pipeline Stable Diffusion.
        """
        try:
            model_id = os.getenv('DYNA_PICTURES_MODEL', 'runwayml/stable-diffusion-v1-5')
            logger.info(f"🚀 Chargement du modèle: {model_id} sur {self.device}")
            
            self.pipeline = DiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            # Remplacer le scheduler par défaut par DDIMScheduler pour éviter les erreurs
            # Le scheduler PNDM et DPMSolver causent des erreurs d'index
            try:
                self.pipeline.scheduler = DDIMScheduler.from_config(
                    self.pipeline.scheduler.config
                )
                logger.info("✅ Scheduler remplacé par DDIMScheduler")
            except Exception as scheduler_e:
                logger.warning(f"⚠️ Impossible de changer le scheduler: {scheduler_e}")
            
            # Optimisations mémoire (seulement si disponibles)
            try:
                if hasattr(self.pipeline, 'enable_attention_slicing'):
                    self.pipeline.enable_attention_slicing()
                if self.device == "cuda" and hasattr(self.pipeline, 'enable_model_cpu_offload'):
                    self.pipeline.enable_model_cpu_offload()
            except Exception as opt_e:
                logger.warning(f"⚠️ Optimisations mémoire non disponibles: {opt_e}")
            
            logger.info("✅ Pipeline chargé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement pipeline: {e}")
            self.pipeline = None

    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Génère une image à partir du prompt fourni par Mistral.
        
        Args:
            prompt (str): Le prompt d'image généré par Mistral
        
        Returns:
            Optional[str]: Le chemin relatif de l'image générée ou None en cas d'échec
        """
        if not self.pipeline:
            logger.error("❌ Pipeline non initialisé")
            return None

        try:
            # Tronquer le prompt si nécessaire pour éviter les erreurs CLIP (max 77 tokens)
            # Le tokenizer de CLIP est interne au pipeline, nous allons donc tronquer le texte brut
            # Une estimation simple est de limiter à environ 500 caractères pour 77 tokens
            # C'est une solution temporaire, une meilleure approche serait d'utiliser le tokenizer réel
            max_prompt_length = 500 # Approximation pour 77 tokens
            
            logger.info(f"Prompt original: {prompt}")
            processed_prompt = prompt[:max_prompt_length] if len(prompt) > max_prompt_length else prompt

            logger.info(f"🎨 Génération avec prompt Mistral (tronqué): {processed_prompt[:100]}...")
            
            try:
                # Exécuter le pipeline de génération d'image
                # Ajout de num_inference_steps pour un contrôle plus fin, valeur par défaut 50
                # Ajout de guidance_scale pour contrôler la force du prompt, valeur par défaut 7.5
                generation_output = self.pipeline(
                    prompt=processed_prompt,
                    negative_prompt="blurry, low quality, distorted, ugly, bad anatomy, text, watermark",
                    num_inference_steps=25, # Optimisé pour DDIMScheduler
                    guidance_scale=7.5, # Force du prompt
                    height=512, # Taille fixe pour éviter les problèmes de dimensions
                    width=512
                )
            except Exception as pipeline_e:
                logger.error(f"❌ Erreur lors de l'exécution du pipeline de génération: {pipeline_e}", exc_info=True)
                return None
            
            # Vérifier si la génération a produit une image valide
            logger.debug(f"Type de generation_output: {type(generation_output)}")
            logger.debug(f"Type de generation_output.images: {type(generation_output.images)}")
            if generation_output.images:
                logger.debug(f"Type de generation_output.images[0]: {type(generation_output.images[0])}")

            if generation_output.images and isinstance(generation_output.images[0], PIL.Image.Image):
                image = generation_output.images[0]
            else:
                logger.error("❌ La génération d'image a échoué: aucune image valide (PIL.Image.Image) retournée.")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cocktail_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image.save(filepath)
            logger.info(f"✅ Image sauvegardée: {filename}")
            
            return f"/cocktail_{timestamp}.png"

        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            return None

    def generate_cocktail_image(self, cocktail_data: dict) -> Optional[str]:
        """
        Génère une image pour un cocktail en utilisant le prompt fourni par Mistral.
        
        Args:
            cocktail_data (dict): Données du cocktail avec 'image_prompt' de Mistral
        
        Returns:
            Optional[str]: Le chemin relatif de l'image générée ou None en cas d'échec
        """
        if not cocktail_data:
            logger.error("❌ Données cocktail manquantes")
            return None
        
        # Utilise le prompt généré par Mistral
        prompt = cocktail_data.get('image_prompt')
        if not prompt:
            logger.error("❌ Prompt d'image Mistral manquant")
            return None
        
        cocktail_name = cocktail_data.get('name', 'Cocktail')
        logger.info(f"🎨 Génération image pour: {cocktail_name}")
        
        return self.generate_image(prompt)
    


    def is_available(self) -> bool:
        """
        Vérifie si le service est disponible.
        """
        return self.pipeline is not None