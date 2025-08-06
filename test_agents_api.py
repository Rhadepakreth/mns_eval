#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'API Mistral Agents avec génération d'images
"""

import os
import requests
import json
from dotenv import load_dotenv

# Charger le fichier .env du backend
load_dotenv('backend/.env')

def test_mistral_agents_image():
    """
    Test de l'API Mistral Agents pour la génération d'images
    """
    print("🧪 Test de l'API Mistral Agents pour la génération d'images\n")
    
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ MISTRAL_API_KEY non configurée")
        return
    
    print(f"✅ Clé API trouvée: {api_key[:10]}...")
    
    try:
        # Étape 1: Créer un agent
        print("\n🔧 Étape 1: Création de l'agent...")
        agent_url = "https://api.mistral.ai/v1/agents"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        agent_data = {
            "model": "mistral-medium-latest",
            "name": "Test Image Agent",
            "description": "Agent de test pour la génération d'images.",
            "instructions": "Utilise l'outil de génération d'images pour créer des images basées sur les descriptions fournies.",
            "tools": [{"type": "image_generation"}],
            "completion_args": {
                "temperature": 0.3,
                "top_p": 0.95
            }
        }
        
        agent_response = requests.post(agent_url, headers=headers, json=agent_data, timeout=30)
        print(f"📊 Status Code Agent: {agent_response.status_code}")
        
        if agent_response.status_code in [200, 201]:
            agent_result = agent_response.json()
            agent_id = agent_result.get('id')
            print(f"✅ Agent créé avec succès: {agent_id}")
            
            # Étape 2: Tester la conversation
            print("\n💬 Étape 2: Test de conversation...")
            conversation_url = "https://api.mistral.ai/v1/conversations"
            conversation_data = {
                "agent_id": agent_id,
                "inputs": "Génère une image d'un cocktail Mojito avec des feuilles de menthe fraîche"
            }
            
            conversation_response = requests.post(conversation_url, headers=headers, json=conversation_data, timeout=60)
            print(f"📊 Status Code Conversation: {conversation_response.status_code}")
            
            if conversation_response.status_code == 200:
                conversation_result = conversation_response.json()
                print("✅ Conversation réussie")
                
                # Chercher le file_id
                outputs = conversation_result.get('outputs', [])
                file_id = None
                
                for output in outputs:
                    if output.get('type') == 'message.output':
                        content = output.get('content', [])
                        for chunk in content:
                            if chunk.get('type') == 'tool_file' and chunk.get('tool') == 'image_generation':
                                file_id = chunk.get('file_id')
                                print(f"🖼️ Image générée avec file_id: {file_id}")
                                break
                        if file_id:
                            break
                
                if file_id:
                    print("✅ Test réussi: Image générée avec succès!")
                else:
                    print("❌ Aucun file_id trouvé dans la réponse")
                    print(f"📄 Réponse complète: {json.dumps(conversation_result, indent=2)}")
            else:
                print(f"❌ Erreur conversation: {conversation_response.text}")
        else:
            print(f"❌ Erreur création agent: {agent_response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n✨ Test terminé")

if __name__ == "__main__":
    test_mistral_agents_image()