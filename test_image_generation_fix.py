#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que la génération d'images fonctionne
après les corrections apportées au service DynaPictures
"""

import requests
import json
import time
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
BASE_URL = "http://127.0.0.1:5001"
FRONTEND_PUBLIC_DIR = "/Users/nicosinus/Dev Web/mns_eval/frontend/public"

def test_cocktail_generation():
    """
    Teste la génération complète d'un cocktail avec image
    """
    print("🧪 Test de génération d'un cocktail avec image...")
    
    # Données de test pour un cocktail
    test_data = {
        "prompt": "Créez un cocktail fruité et coloré avec de la vodka, du jus de cranberry et du jus de citron vert pour une soirée entre amis"
    }
    
    try:
        # 1. Générer le cocktail
        print("📝 Génération du cocktail...")
        response = requests.post(f"{BASE_URL}/api/cocktails/generate", json=test_data)
        
        if response.status_code not in [200, 201]:
            print(f"❌ Erreur génération cocktail: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
        response_data = response.json()
        cocktail_data = response_data.get('cocktail', response_data)  # Support des deux formats
        print(f"✅ Cocktail généré: {cocktail_data.get('name', 'Sans nom')}")
        print(f"📋 Prompt d'image: {cocktail_data.get('image_prompt', 'Aucun')[:100]}...")
        
        # 2. Générer l'image pour ce cocktail
        print("🎨 Génération de l'image...")
        cocktail_id = cocktail_data.get('id')
        if not cocktail_id:
            print("❌ Erreur: ID du cocktail non trouvé")
            return False
            
        image_data = {"cocktail_id": cocktail_id}
        # Timeout plus long pour la génération d'images (10 minutes)
        image_response = requests.post(f"{BASE_URL}/api/cocktails/generate-image", json=image_data, timeout=600)
        
        if image_response.status_code != 200:
            print(f"❌ Erreur génération image: {image_response.status_code}")
            print(f"Réponse: {image_response.text}")
            return False
            
        image_result = image_response.json()
        print(f"📊 Réponse génération image: {image_result}")
        
        if not image_result.get('success', False):
            print(f"❌ Génération d'image échouée: {image_result.get('error', 'Erreur inconnue')}")
            return False
            
        image_path = image_result.get('image_url')
        if not image_path:
            print("❌ Aucun chemin d'image retourné")
            return False
            
        print(f"✅ Image générée: {image_path}")
        
        # 3. Vérifier que l'image existe physiquement
        if image_path.startswith('/'):
            # Chemin relatif, construire le chemin complet
            full_image_path = os.path.join(FRONTEND_PUBLIC_DIR, image_path.lstrip('/'))
        else:
            full_image_path = os.path.join(FRONTEND_PUBLIC_DIR, image_path)
            
        if os.path.exists(full_image_path):
            file_size = os.path.getsize(full_image_path)
            print(f"✅ Fichier image trouvé: {full_image_path} ({file_size} bytes)")
            
            # Vérifier que ce n'est pas l'image par défaut
            if "default.webp" in image_path:
                print("⚠️ Image par défaut utilisée - la génération a échoué")
                return False
            else:
                print("🎉 Image personnalisée générée avec succès !")
                return True
        else:
            print(f"❌ Fichier image non trouvé: {full_image_path}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Flask")
        print("Vérifiez que le serveur est démarré sur http://127.0.0.1:5001")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_image_service_status():
    """
    Teste le statut du service d'image
    """
    print("🔍 Vérification du statut du service d'image...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Statut du service: {status}")
            # Vérifier dans la structure services
            services = status.get('services', {})
            return services.get('image_service_available', False)
        else:
            print(f"❌ Erreur statut: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur vérification statut: {e}")
        return False

def main():
    """
    Fonction principale de test
    """
    print("🚀 Début des tests de génération d'images")
    print("=" * 50)
    
    # Test 1: Statut du service
    service_ok = test_image_service_status()
    print()
    
    if not service_ok:
        print("❌ Service d'image non disponible, arrêt des tests")
        return
    
    # Test 2: Génération complète
    generation_ok = test_cocktail_generation()
    print()
    
    # Résumé
    print("=" * 50)
    if generation_ok:
        print("🎉 SUCCÈS: La génération d'images fonctionne parfaitement !")
        print("✅ Les corrections du scheduler DPMSolverMultistepScheduler sont efficaces")
    else:
        print("❌ ÉCHEC: Des problèmes persistent dans la génération d'images")
        print("🔧 Vérifiez les logs du serveur Flask pour plus de détails")

if __name__ == "__main__":
    main()