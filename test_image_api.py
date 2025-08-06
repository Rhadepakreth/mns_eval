#!/usr/bin/env python3
"""
Script de test pour l'endpoint de génération d'image
"""

import requests
import json

def test_image_generation():
    """
    Teste l'endpoint de génération d'image
    """
    url = 'http://localhost:5002/api/cocktails/generate-image'
    
    # Données de test
    data = {
        'prompt': 'Un cocktail coloré dans un verre à martini avec une décoration de fruits'
    }
    
    try:
        print("Test de génération d'image...")
        print(f"URL: {url}")
        print(f"Prompt: {data['prompt']}")
        print()
        
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 503:
            print("\n✅ Service correctement configuré pour retourner un message d'indisponibilité")
        elif response.status_code == 200:
            print("\n✅ Image générée avec succès")
        else:
            print(f"\n❌ Code de statut inattendu: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == '__main__':
    test_image_generation()