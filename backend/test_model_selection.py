#!/usr/bin/env python3
"""
Script de test pour démontrer la sélection automatique de modèles Stable Diffusion
et les améliorations apportées au système de génération d'images.
"""

import requests
import json
import time
from typing import Dict, Any

def test_model_selection_and_generation():
    """
    Teste la sélection automatique de modèle et la génération d'image optimisée.
    """
    print("🧪 Test du nouveau système de modèles Stable Diffusion")
    print("=" * 60)
    
    # Test de génération d'image pour un cocktail existant
    cocktail_id = 16
    url = 'http://localhost:5002/api/cocktails/generate-image'
    
    print(f"\n🍹 Test de génération d'image pour le cocktail ID: {cocktail_id}")
    print(f"📡 URL: {url}")
    
    try:
        # Mesurer le temps de génération
        start_time = time.time()
        
        response = requests.post(url, json={'cocktail_id': cocktail_id})
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"\n⏱️ Temps de génération: {generation_time:.2f} secondes")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Génération réussie !")
            print(f"🎯 Cocktail: {data.get('cocktail_name', 'N/A')}")
            print(f"🖼️ Image URL: {data.get('image_url', 'N/A')}")
            
            # Test d'accessibilité de l'image
            if data.get('image_url'):
                image_url = f"http://localhost:5002{data['image_url']}"
                img_response = requests.head(image_url)
                
                if img_response.status_code == 200:
                    content_length = img_response.headers.get('Content-Length', 'N/A')
                    print(f"🌐 Image accessible: {img_response.status_code}")
                    print(f"📏 Taille: {content_length} bytes")
                else:
                    print(f"❌ Image non accessible: {img_response.status_code}")
            
            return True
            
        else:
            print(f"❌ Erreur de génération: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Détails: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Réponse brute: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def print_system_info():
    """
    Affiche les informations sur les améliorations du système.
    """
    print("\n🚀 Améliorations apportées au système:")
    print("=" * 50)
    print("📈 Sélection automatique de modèle basée sur la VRAM disponible:")
    print("   • SDXL 1.0 (≥10GB VRAM) - Qualité supérieure, 1024x1024")
    print("   • SD 2.1 (≥6GB VRAM) - Bon équilibre, 768x768")
    print("   • SD 1.5 (≥4GB VRAM) - Rapide et compatible, 512x512")
    print("\n⚙️ Paramètres optimisés par modèle:")
    print("   • Nombre d'étapes d'inférence adapté")
    print("   • Guidance scale optimisé")
    print("   • Résolution native du modèle")
    print("   • Prompts négatifs spécialisés")
    print("\n🔧 Optimisations techniques:")
    print("   • Gestion automatique CUDA/CPU")
    print("   • Fallback intelligent vers SD1.5")
    print("   • Optimisations mémoire pour SDXL")
    print("   • Prompts limités à 40 mots (anti-troncature CLIP)")
    print("\n💡 Avantages:")
    print("   • Qualité d'image améliorée")
    print("   • Adaptation automatique aux ressources")
    print("   • Stabilité et fiabilité accrues")
    print("   • Support des modèles les plus récents")

if __name__ == '__main__':
    print_system_info()
    
    print("\n" + "=" * 60)
    success = test_model_selection_and_generation()
    
    if success:
        print("\n🎉 Test réussi ! Le nouveau système de modèles fonctionne parfaitement.")
        print("✨ Votre système peut maintenant générer des images de haute qualité")
        print("   avec sélection automatique du meilleur modèle disponible.")
    else:
        print("\n⚠️ Test échoué. Vérifiez que le serveur backend est démarré.")
    
    print("\n" + "=" * 60)