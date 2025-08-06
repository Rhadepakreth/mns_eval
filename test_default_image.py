#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage de l'image par défaut
"""

import requests
import json

def test_cocktail_with_default_image():
    """
    Teste la génération d'un cocktail et vérifie que l'image par défaut s'affiche
    """
    # 1. Générer un nouveau cocktail
    cocktail_url = 'http://localhost:5002/api/cocktails/generate'
    cocktail_data = {
        'prompt': 'Un cocktail tropical pour tester l\'image par défaut'
    }
    
    print("🍹 Génération d'un nouveau cocktail...")
    response = requests.post(cocktail_url, json=cocktail_data)
    
    if response.status_code != 201:
        print(f"❌ Erreur lors de la génération du cocktail: {response.status_code}")
        return
    
    cocktail = response.json()['cocktail']
    print(f"✅ Cocktail généré: {cocktail['name']}")
    print(f"📝 Prompt d'image: {cocktail.get('image_prompt', 'Aucun')}")
    
    # 2. Tenter de générer l'image (qui devrait échouer)
    if cocktail.get('image_prompt'):
        image_url = 'http://localhost:5002/api/cocktails/generate-image'
        image_data = {
            'prompt': cocktail['image_prompt']
        }
        
        print("\n🖼️ Tentative de génération d'image...")
        image_response = requests.post(image_url, json=image_data)
        
        print(f"Status Code: {image_response.status_code}")
        print(f"Response: {json.dumps(image_response.json(), indent=2, ensure_ascii=False)}")
        
        if image_response.status_code == 503:
            print("\n✅ Génération d'image indisponible comme attendu")
            print("✅ L'image par défaut devrait maintenant s'afficher dans l'interface")
        else:
            print(f"\n❌ Code de statut inattendu: {image_response.status_code}")
    
    # 3. Vérifier que l'image par défaut est accessible
    print("\n🔍 Vérification de l'accessibilité de l'image par défaut...")
    default_image_response = requests.head('http://localhost:5173/default.webp')
    
    if default_image_response.status_code == 200:
        print("✅ Image par défaut accessible")
        print(f"📏 Taille: {default_image_response.headers.get('Content-Length', 'Inconnue')} bytes")
        print(f"📄 Type: {default_image_response.headers.get('Content-Type', 'Inconnu')}")
    else:
        print(f"❌ Image par défaut non accessible: {default_image_response.status_code}")
    
    print(f"\n🎯 Cocktail ID: {cocktail['id']}")
    print("💡 Vous pouvez maintenant aller voir le cocktail dans l'interface pour vérifier l'affichage de l'image par défaut")

if __name__ == '__main__':
    test_cocktail_with_default_image()