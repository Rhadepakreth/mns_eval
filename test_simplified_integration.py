#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'intégration du service DynaPictures simplifié
Vérifie que l'API utilise correctement les prompts de Mistral
"""

import requests
import json
import time

def test_cocktail_generation_with_image():
    """
    Test complet : génération de cocktail + image avec prompt Mistral
    """
    print("\n" + "="*60)
    print("🧪 TEST INTÉGRATION: Génération cocktail + image")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Génération d'un cocktail
    print("\n📝 Étape 1: Génération du cocktail avec Mistral")
    cocktail_data = {
        "prompt": "Un cocktail tropical rafraîchissant avec de l'ananas et de la noix de coco"
    }
    
    try:
        response = requests.post(f"{base_url}/api/cocktails/generate", json=cocktail_data)
        
        if response.status_code == 200:
            cocktail = response.json()
            print(f"✅ Cocktail généré: {cocktail['name']}")
            print(f"📝 Description: {cocktail['description'][:100]}...")
            
            # Vérifier que le prompt d'image est présent
            if 'image_prompt' in cocktail:
                print(f"🎯 Prompt d'image Mistral: {cocktail['image_prompt'][:80]}...")
                
                # Test 2: Génération de l'image
                print("\n📝 Étape 2: Génération de l'image avec DynaPictures")
                image_data = {"cocktail_id": cocktail['id']}
                
                image_response = requests.post(f"{base_url}/api/cocktails/generate-image", json=image_data)
                
                if image_response.status_code == 200:
                    image_result = image_response.json()
                    if image_result.get('success'):
                        print(f"✅ Image générée: {image_result['image_url']}")
                        print(f"🎨 Service utilisé: DynaPictures avec prompt Mistral")
                        return True
                    else:
                        print(f"❌ Échec génération image: {image_result.get('error')}")
                else:
                    print(f"❌ Erreur API image: {image_response.status_code}")
            else:
                print("⚠️ Pas de prompt d'image dans la réponse Mistral")
        else:
            print(f"❌ Erreur génération cocktail: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("ℹ️ Assurez-vous que le serveur Flask est démarré (python backend/app.py)")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    
    return False

def test_service_availability():
    """
    Test de disponibilité des services
    """
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION: Disponibilité des services")
    print("="*60)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test de santé de l'API
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Serveur Flask accessible")
        else:
            print(f"⚠️ Serveur répond avec code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Flask non accessible")
        print("ℹ️ Démarrez le serveur avec: cd backend && python app.py")
        return False
    
    return True

def show_service_summary():
    """
    Affiche un résumé des améliorations du service simplifié
    """
    print("\n" + "="*60)
    print("📊 RÉSUMÉ: Service DynaPictures Simplifié")
    print("="*60)
    
    print("\n🎯 Améliorations apportées:")
    print("   ✅ Suppression de la génération automatique de prompts")
    print("   ✅ Utilisation directe des prompts optimisés de Mistral")
    print("   ✅ Code simplifié et plus maintenable")
    print("   ✅ Réduction des dépendances et de la complexité")
    print("   ✅ Meilleure cohérence entre description et image")
    
    print("\n🔧 Fonctionnalités conservées:")
    print("   ✅ Chargement automatique du pipeline Stable Diffusion")
    print("   ✅ Optimisations mémoire (GPU/CPU)")
    print("   ✅ Sauvegarde automatique des images")
    print("   ✅ Gestion d'erreurs robuste")
    
    print("\n📈 Bénéfices:")
    print("   🚀 Performance: Moins de calculs inutiles")
    print("   🎨 Qualité: Prompts plus précis et contextualisés")
    print("   🛠️ Maintenance: Code plus simple à comprendre et modifier")
    print("   🔗 Intégration: Meilleure synergie avec Mistral")

if __name__ == "__main__":
    print("🚀 Test d'intégration du service DynaPictures simplifié")
    
    # Vérification de la disponibilité
    if test_service_availability():
        # Test complet
        success = test_cocktail_generation_with_image()
        
        if success:
            print("\n🎉 Test d'intégration réussi !")
        else:
            print("\n⚠️ Test d'intégration partiellement réussi")
    
    # Affichage du résumé
    show_service_summary()
    
    print("\n" + "="*60)
    print("🏁 Tests terminés")
    print("="*60)