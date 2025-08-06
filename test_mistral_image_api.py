#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'API Mistral pour la génération d'images

Ce script teste l'endpoint de génération d'images de Mistral
pour vérifier si l'API est disponible et fonctionnelle.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Charger le fichier .env du backend
load_dotenv('backend/.env')

def test_mistral_image_api():
    """
    Teste l'API de génération d'images Mistral
    """
    # Configuration
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ MISTRAL_API_KEY non configurée")
        return False
    
    api_url = 'https://api.mistral.ai/v1/generate-image'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': 'Un cocktail coloré dans un verre élégant avec des fruits tropicaux',
        'model': 'pixtral-12b-2409',
        'size': '1024x1024',
        'quality': 'standard'
    }
    
    print(f"🔍 Test de l'API Mistral Image: {api_url}")
    print(f"📝 Prompt: {data['prompt']}")
    print(f"🤖 Modèle: {data['model']}")
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Succès!")
            print(f"📄 Réponse: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"📄 Réponse: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout de la requête")
        return False
    except requests.exceptions.RequestException as e:
        print(f"🌐 Erreur de requête: {str(e)}")
        return False
    except Exception as e:
        print(f"💥 Erreur inattendue: {str(e)}")
        return False

def test_alternative_endpoints():
    """
    Teste des endpoints alternatifs possibles
    """
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        return
    
    alternative_urls = [
        'https://api.mistral.ai/v1/images/generations',
        'https://api.mistral.ai/v1/images/generate',
        'https://api.mistral.ai/v1/chat/completions'  # Pour vérifier si l'API fonctionne
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    for url in alternative_urls:
        print(f"\n🔍 Test de l'endpoint: {url}")
        try:
            if 'chat/completions' in url:
                # Test simple de l'API chat pour vérifier la connectivité
                data = {
                    'model': 'mistral-large-latest',
                    'messages': [{'role': 'user', 'content': 'Hello'}],
                    'max_tokens': 10
                }
            else:
                # Test pour les endpoints d'images
                data = {
                    'prompt': 'Un cocktail coloré',
                    'model': 'pixtral-12b-2409',
                    'size': '1024x1024'
                }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code != 404:
                print(f"📄 Réponse: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")

if __name__ == '__main__':
    print("🧪 Test de l'API Mistral pour la génération d'images\n")
    
    # Test principal
    success = test_mistral_image_api()
    
    if not success:
        print("\n🔄 Test des endpoints alternatifs...")
        test_alternative_endpoints()
    
    print("\n✨ Test terminé")