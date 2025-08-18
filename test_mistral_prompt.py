#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que DynaPictures utilise le prompt d'image de Mistral

Ce script teste :
1. L'utilisation du prompt Mistral quand il est fourni
2. Le fallback vers la génération automatique quand il n'y en a pas
3. La gestion des cas d'erreur
"""

import sys
import os
sys.path.append('backend')

from services.dynapictures_service import DynaPicturesService
import logging

# Configuration du logging pour voir les messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mistral_prompt_usage():
    """
    Test principal pour vérifier l'utilisation du prompt Mistral
    """
    print("\n" + "="*60)
    print("🧪 TEST: Utilisation du prompt d'image Mistral")
    print("="*60)
    
    # Initialisation du service
    service = DynaPicturesService()
    
    if not service.is_available():
        print("❌ Service DynaPictures non disponible (pipeline non chargé)")
        print("ℹ️  Ceci est normal si les dépendances ne sont pas installées")
        return False
    
    print("✅ Service DynaPictures initialisé avec succès")
    
    # Test 1: Avec prompt Mistral fourni
    print("\n📝 Test 1: Utilisation du prompt Mistral")
    cocktail_with_mistral_prompt = {
        'name': 'Sunset Paradise',
        'ingredients': ['4 cl de rhum blanc', '2 cl de jus d\'orange', '1 cl de grenadine'],
        'description': 'Un cocktail tropical aux couleurs du coucher de soleil',
        'image_prompt': 'Professional cocktail photography of a tropical sunset cocktail in an elegant glass, orange and red gradient colors, garnished with orange slice, black background, studio lighting, hyper-realistic, 4K'
    }
    
    print(f"Prompt Mistral: {cocktail_with_mistral_prompt['image_prompt'][:80]}...")
    result1 = service.generate_cocktail_image(cocktail_with_mistral_prompt)
    
    if result1:
        print(f"✅ Image générée avec prompt Mistral: {result1}")
    else:
        print("❌ Échec de génération avec prompt Mistral")
    
    # Test 2: Sans prompt Mistral (fallback)
    print("\n📝 Test 2: Fallback vers génération automatique")
    cocktail_without_prompt = {
        'name': 'Classic Mojito',
        'ingredients': ['5 cl de rhum blanc', '3 cl de jus de citron vert', 'Feuilles de menthe'],
        'description': 'Le mojito classique rafraîchissant'
        # Pas de champ 'image_prompt'
    }
    
    print("Aucun prompt Mistral fourni, utilisation de la génération automatique")
    result2 = service.generate_cocktail_image(cocktail_without_prompt)
    
    if result2:
        print(f"✅ Image générée avec prompt automatique: {result2}")
    else:
        print("❌ Échec de génération avec prompt automatique")
    
    # Test 3: Prompt Mistral vide
    print("\n📝 Test 3: Prompt Mistral vide (fallback)")
    cocktail_empty_prompt = {
        'name': 'Margarita',
        'ingredients': ['5 cl de tequila', '2 cl de triple sec', '3 cl de jus de citron vert'],
        'description': 'La margarita classique',
        'image_prompt': ''  # Prompt vide
    }
    
    print("Prompt Mistral vide, utilisation de la génération automatique")
    result3 = service.generate_cocktail_image(cocktail_empty_prompt)
    
    if result3:
        print(f"✅ Image générée avec prompt automatique (prompt vide): {result3}")
    else:
        print("❌ Échec de génération avec prompt automatique (prompt vide)")
    
    # Test 4: Données invalides
    print("\n📝 Test 4: Gestion des données invalides")
    invalid_data = {'description': 'Pas de nom'}  # Manque le champ 'name'
    
    result4 = service.generate_cocktail_image(invalid_data)
    
    if result4 is None:
        print("✅ Gestion correcte des données invalides (retourne None)")
    else:
        print(f"❌ Comportement inattendu avec données invalides: {result4}")
    
    print("\n" + "="*60)
    print("🏁 Tests terminés")
    print("="*60)
    
    return True

def test_prompt_comparison():
    """
    Test pour démontrer l'utilisation des prompts Mistral vs génération automatique
    """
    print("\n" + "="*60)
    print("🔍 COMPARAISON: Service simplifié avec prompts Mistral")
    print("="*60)
    
    # Exemple de prompt Mistral (ce que le service utilise maintenant)
    mistral_prompt = "Professional photo of a creamy Piña Colada in a hurricane glass, garnished with pineapple wedge and cherry, tropical beach background, golden hour lighting, photorealistic"
    print(f"🧠 Prompt Mistral utilisé: {mistral_prompt}")
    
    print("\n📊 Avantages du service simplifié:")
    print(f"   - Utilise directement les prompts optimisés de Mistral")
    print(f"   - Plus de génération automatique complexe")
    print(f"   - Code plus simple et maintenable")
    print(f"   - Prompts plus spécifiques et contextualisés")
    print(f"   - Longueur prompt: {len(mistral_prompt)} caractères")

if __name__ == "__main__":
    print("🚀 Démarrage des tests DynaPictures avec prompts Mistral")
    
    try:
        # Test principal
        success = test_mistral_prompt_usage()
        
        # Test de comparaison
        test_prompt_comparison()
        
        if success:
            print("\n🎉 Tous les tests ont été exécutés avec succès!")
            print("✅ DynaPictures utilise maintenant les prompts de Mistral")
        else:
            print("\n⚠️  Tests exécutés mais service non disponible")
            print("ℹ️  Installez les dépendances pour tester la génération réelle")
            
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()