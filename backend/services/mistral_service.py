#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service d'intégration avec l'API Mistral pour Le Mixologue Augmenté

Gère la communication avec l'API Mistral pour générer des fiches cocktails
basées sur les demandes des utilisateurs. Optimise les prompts pour obtenir
des réponses structurées et créatives.

Auteur: Assistant IA
Date: 2024
"""

import os
import json
import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MistralService:
    """
    Service pour l'intégration avec l'API Mistral.
    
    Gère la génération de cocktails via l'IA Mistral en optimisant
    les prompts pour obtenir des réponses structurées et créatives.
    """
    
    def __init__(self):
        """
        Initialise le service Mistral avec la configuration.
        
        Raises:
            ValueError: Si la clé API Mistral n'est pas configurée
        """
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY non configurée. "
                "Veuillez définir cette variable d'environnement."
            )
        
        self.model = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
        self.base_url = 'https://api.mistral.ai/v1/chat/completions'
        self.timeout = 30  # Timeout en secondes
        self.max_retries = 3
        
        logger.info(f"Service Mistral initialisé avec le modèle: {self.model}")
    
    def _build_system_prompt(self) -> str:
        """
        Construit le prompt système optimisé pour la génération de cocktails.
        
        Returns:
            str: Prompt système détaillé
        """
        return """
Tu es un mixologue expert et créatif travaillant dans un bar à cocktails haut de gamme à Metz. 
Ton rôle est de créer des cocktails originaux et personnalisés selon les demandes des clients.

Pour chaque demande, tu dois générer une fiche cocktail complète au format JSON strict suivant :

{
  "name": "Nom créatif et original du cocktail",
  "ingredients": [
    "Quantité précise + Ingrédient 1",
    "Quantité précise + Ingrédient 2",
    "..."
  ],
  "description": "Histoire courte et engageante du cocktail (2-3 phrases max)",
  "music_ambiance": "Suggestion d'ambiance musicale adaptée au cocktail",
  "image_prompt": "Prompt détaillé pour générer une image du cocktail avec MidJourney/SDXL"
}

Règles importantes :
1. Le nom doit être original, créatif et évocateur
2. Les ingrédients doivent inclure des quantités précises (cl, ml, traits, etc.)
3. La description doit raconter une histoire ou donner du contexte
4. L'ambiance musicale doit correspondre à l'esprit du cocktail
5. Le prompt image doit être détaillé pour une belle photo de cocktail
6. Réponds UNIQUEMENT en JSON valide, sans texte supplémentaire
7. Adapte-toi aux goûts, contraintes et contexte mentionnés par le client
8. Sois créatif mais réaliste dans les associations d'ingrédients
"""
    
    def _build_user_prompt(self, user_request: str) -> str:
        """
        Construit le prompt utilisateur à partir de la demande.
        
        Args:
            user_request (str): Demande de l'utilisateur
        
        Returns:
            str: Prompt utilisateur formaté
        """
        return f"""
Demande du client : "{user_request}"

Crée un cocktail personnalisé qui répond parfaitement à cette demande.
Réponds uniquement avec le JSON de la fiche cocktail.
"""
    
    def _make_api_request(self, messages: list) -> Optional[Dict[str, Any]]:
        """
        Effectue une requête à l'API Mistral avec gestion des erreurs.
        
        Args:
            messages (list): Messages pour l'API Mistral
        
        Returns:
            Optional[Dict]: Réponse de l'API ou None en cas d'erreur
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.8,  # Créativité élevée
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentative {attempt + 1}/{self.max_retries} d'appel à l'API Mistral")
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                data = response.json()
                logger.info("Réponse reçue de l'API Mistral avec succès")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout lors de la tentative {attempt + 1}")
                if attempt == self.max_retries - 1:
                    logger.error("Échec définitif : timeout de l'API Mistral")
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"Erreur HTTP {e.response.status_code}: {e.response.text}")
                if e.response.status_code == 401:
                    logger.error("Clé API Mistral invalide")
                    break
                elif e.response.status_code == 429:
                    logger.warning("Limite de taux atteinte, nouvelle tentative...")
                    continue
                else:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur de requête: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Échec définitif de la requête")
                    
            except Exception as e:
                logger.error(f"Erreur inattendue: {str(e)}")
                break
        
        return None
    
    def _parse_cocktail_response(self, api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse la réponse de l'API Mistral pour extraire les données du cocktail.
        
        Args:
            api_response (Dict): Réponse brute de l'API Mistral
        
        Returns:
            Optional[Dict]: Données du cocktail parsées ou None en cas d'erreur
        """
        try:
            # Extraction du contenu de la réponse
            if 'choices' not in api_response or not api_response['choices']:
                logger.error("Réponse API Mistral invalide: pas de 'choices'")
                return None
            
            content = api_response['choices'][0]['message']['content']
            logger.debug(f"Contenu brut de Mistral: {content}")
            
            # Nettoyage du contenu (suppression des balises markdown si présentes)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse du JSON
            cocktail_data = json.loads(content)
            
            # Validation des champs requis
            required_fields = ['name', 'ingredients', 'description', 'music_ambiance']
            for field in required_fields:
                if field not in cocktail_data:
                    logger.error(f"Champ requis manquant: {field}")
                    return None
            
            # Validation des types
            if not isinstance(cocktail_data['ingredients'], list):
                logger.error("Le champ 'ingredients' doit être une liste")
                return None
            
            # Ajout du champ image_prompt s'il est manquant
            if 'image_prompt' not in cocktail_data:
                cocktail_data['image_prompt'] = self._generate_default_image_prompt(
                    cocktail_data['name']
                )
            
            logger.info(f"Cocktail parsé avec succès: {cocktail_data['name']}")
            return cocktail_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {str(e)}")
            logger.error(f"Contenu reçu: {content[:200]}...")
            return None
            
        except KeyError as e:
            logger.error(f"Structure de réponse inattendue: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing de la réponse: {str(e)}")
            return None
    
    def _generate_default_image_prompt(self, cocktail_name: str) -> str:
        """
        Génère un prompt image par défaut si Mistral n'en fournit pas.
        
        Args:
            cocktail_name (str): Nom du cocktail
        
        Returns:
            str: Prompt image par défaut
        """
        return f"""
Photo professionnelle du cocktail "{cocktail_name}" dans un verre élégant, 
éclairage tamisé de bar, arrière-plan flou, style gastronomique, 
hyper-réaliste, 4K, composition esthétique
"""
    
    def generate_cocktail(self, user_request: str) -> Optional[Dict[str, Any]]:
        """
        Génère un cocktail basé sur la demande de l'utilisateur.
        
        Args:
            user_request (str): Demande de l'utilisateur
        
        Returns:
            Optional[Dict]: Données du cocktail généré ou None en cas d'erreur
        """
        if not user_request or not user_request.strip():
            logger.error("Demande utilisateur vide")
            return None
        
        logger.info(f"Génération d'un cocktail pour: {user_request[:100]}...")
        
        # Construction des messages pour l'API
        messages = [
            {
                'role': 'system',
                'content': self._build_system_prompt()
            },
            {
                'role': 'user',
                'content': self._build_user_prompt(user_request)
            }
        ]
        
        # Appel à l'API Mistral
        api_response = self._make_api_request(messages)
        if not api_response:
            logger.error("Échec de l'appel à l'API Mistral")
            return None
        
        # Parse de la réponse
        cocktail_data = self._parse_cocktail_response(api_response)
        if not cocktail_data:
            logger.error("Échec du parsing de la réponse Mistral")
            return None
        
        logger.info(f"Cocktail généré avec succès: {cocktail_data['name']}")
        return cocktail_data
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'API Mistral.
        
        Returns:
            bool: True si la connexion fonctionne, False sinon
        """
        try:
            logger.info("Test de connexion à l'API Mistral...")
            
            test_messages = [
                {
                    'role': 'user',
                    'content': 'Réponds simplement "OK" pour tester la connexion.'
                }
            ]
            
            response = self._make_api_request(test_messages)
            
            if response and 'choices' in response:
                logger.info("Test de connexion Mistral réussi")
                return True
            else:
                logger.error("Test de connexion Mistral échoué")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du test de connexion: {str(e)}")
            return False
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Génère une image à partir d'un prompt en utilisant l'API Mistral Agents.
        Cette méthode utilise l'API Agents avec le connecteur image_generation.
        
        Args:
            prompt (str): Prompt de description de l'image
        
        Returns:
            Optional[str]: Chemin relatif de l'image générée ou None
        """
        if not prompt or not prompt.strip():
            logger.error("Prompt d'image vide")
            return None
        
        logger.info(f"Génération d'image pour: {prompt[:100]}...")
        
        try:
            # Étape 1: Créer un agent avec le connecteur image_generation
            agent_url = "https://api.mistral.ai/v1/agents"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            agent_data = {
                "model": "mistral-medium-latest",
                "name": "Image Generation Agent",
                "description": "Agent utilisé pour générer des images de cocktails.",
                "instructions": "Utilise l'outil de génération d'images pour créer des images de cocktails basées sur les descriptions fournies.",
                "tools": [{"type": "image_generation"}],
                "completion_args": {
                    "temperature": 0.3,
                    "top_p": 0.95
                }
            }
            
            logger.info("Création de l'agent pour la génération d'image...")
            agent_response = requests.post(agent_url, headers=headers, json=agent_data, timeout=30)
            
            if agent_response.status_code not in [200, 201]:
                logger.error(f"Erreur lors de la création de l'agent: {agent_response.status_code} - {agent_response.text}")
                return None
                
            agent_result = agent_response.json()
            agent_id = agent_result.get('id')
            
            if not agent_id:
                logger.error(f"Erreur: ID de l'agent non trouvé dans la réponse - {agent_result}")
                return None
            
            logger.info(f"Agent créé avec l'ID: {agent_id}")
            
            # Étape 2: Démarrer une conversation avec l'agent
            conversation_url = "https://api.mistral.ai/v1/conversations"
            conversation_data = {
                "agent_id": agent_id,
                "inputs": f"Génère une image de cocktail basée sur cette description: {prompt}"
            }
            
            logger.info("Démarrage de la conversation pour générer l'image...")
            conversation_response = requests.post(conversation_url, headers=headers, json=conversation_data, timeout=60)
            
            if conversation_response.status_code != 200:
                logger.error(f"Erreur lors de la conversation: {conversation_response.status_code} - {conversation_response.text}")
                return None
                
            conversation_result = conversation_response.json()
            
            # Étape 3: Extraire le file_id de l'image générée
            outputs = conversation_result.get('outputs', [])
            file_id = None
            
            for output in outputs:
                if output.get('type') == 'message.output':
                    content = output.get('content', [])
                    for chunk in content:
                        if chunk.get('type') == 'tool_file' and chunk.get('tool') == 'image_generation':
                            file_id = chunk.get('file_id')
                            break
                    if file_id:
                        break
            
            if not file_id:
                logger.error(f"Erreur: Aucun file_id trouvé dans la réponse - {conversation_result}")
                return None
            
            logger.info(f"Image générée avec le file_id: {file_id}")
            
            # Étape 4: Télécharger l'image et la sauvegarder localement
            download_url = f"https://api.mistral.ai/v1/files/{file_id}/download"
            download_response = requests.get(download_url, headers=headers, timeout=30)
            
            if download_response.status_code != 200:
                logger.error(f"Erreur lors du téléchargement: {download_response.status_code} - {download_response.text}")
                return None
            
            # Sauvegarder l'image dans le dossier public du frontend
            # Créer un nom de fichier unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cocktail_generated_{timestamp}.png"
            
            # Chemin vers le dossier public du frontend
            frontend_public_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'public')
            file_path = os.path.join(frontend_public_path, filename)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder l'image
            with open(file_path, 'wb') as f:
                f.write(download_response.content)
            
            logger.info(f"Image sauvegardée: {file_path}")
            
            # Retourner l'URL relative pour le frontend
            return f"/{filename}"
            
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la génération d'image")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête lors de la génération d'image: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la génération d'image: {str(e)}")
        
        return None