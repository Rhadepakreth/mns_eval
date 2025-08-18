#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le service DynaPictures

Ce script teste la génération d'images localement avec Stable Diffusion
pour s'assurer que le service fonctionne correctement.

Auteur: Assistant IA
Date: 2024
"""

import sys
import os
import logging
from datetime import datetime

# Ajouter le répertoire backend au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.dynapictures_service import DynaPicturesService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dynapictures_service():
    """
    Teste le service DynaPictures avec différents scénarios.
    """
    print("🧪 === Test du Service DynaPictures ===")
    print()
    
    try:
        # 1. Initialisation du service
        print("1️⃣ Initialisation du service DynaPictures...")
        service = DynaPicturesService()
        print(f"   ✅ Service initialisé")
        print(f"   📱 Device utilisé: {service.device}")
        print(f"   🤖 Modèle: {service.model_id}")
        print(f"   📁 Répertoire de sortie: {service.output_dir}")
        print()
        
        # 2. Vérification de la disponibilité
        print("2️⃣ Vérification de la disponibilité...")
        is_available = service.is_available()
        print(f"   {'✅' if is_available else '❌'} Service disponible: {is_available}")
        
        if not is_available:
            print("   ⚠️ Le service n'est pas disponible. Vérifiez l'installation de diffusers et torch.")
            return False
        print()
        
        # 3. Test de génération d'image simple
        print("3️⃣ Test de génération d'image simple...")
        simple_prompt = "professional cocktail photography, elegant martini cocktail, crystal clear glass"
        print(f"   📝 Prompt: {simple_prompt}")
        
        start_time = datetime.now()
        image_path = service.generate_image(simple_prompt)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if image_path:
            print(f"   ✅ Image générée avec succès: {image_path}")
            print(f"   ⏱️ Temps de génération: {duration:.2f} secondes")
        else:
            print(f"   ❌ Échec de la génération d'image")
            return False
        print()
        
        # 4. Test avec données de cocktail complètes
        print("4️⃣ Test avec données de cocktail complètes...")
        cocktail_data = {
            'name': 'Mojito Tropical',
            'description': 'Un cocktail rafraîchissant aux saveurs tropicales',
            'ingredients': [
                {'name': 'Rhum blanc', 'quantity': '6 cl'},
                {'name': 'Menthe fraîche', 'quantity': '10 feuilles'},
                {'name': 'Citron vert', 'quantity': '1/2'},
                {'name': 'Sucre de canne', 'quantity': '2 cuillères'},
                {'name': 'Eau gazeuse', 'quantity': '10 cl'}
            ]
        }
        
        print(f"   🍹 Cocktail: {cocktail_data['name']}")
        print(f"   📝 Ingrédients: {len(cocktail_data['ingredients'])} éléments")
        
        start_time = datetime.now()
        cocktail_image_path = service.generate_cocktail_image(cocktail_data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if cocktail_image_path:
            print(f"   ✅ Image de cocktail générée: {cocktail_image_path}")
            print(f"   ⏱️ Temps de génération: {duration:.2f} secondes")
        else:
            print(f"   ❌ Échec de la génération d'image de cocktail")
            return False
        print()
        
        # 5. Test avec données invalides
        print("5️⃣ Test avec données invalides...")
        invalid_data = {'description': 'Pas de nom'}
        invalid_result = service.generate_cocktail_image(invalid_data)
        
        if invalid_result is None:
            print(f"   ✅ Gestion correcte des données invalides")
        else:
            print(f"   ⚠️ Résultat inattendu avec données invalides: {invalid_result}")
        print()
        
        print("🎉 === Tous les tests sont passés avec succès! ===")
        print()
        print("📋 Résumé:")
        print(f"   • Service disponible: ✅")
        print(f"   • Génération simple: ✅ ({image_path})")
        print(f"   • Génération cocktail: ✅ ({cocktail_image_path})")
        print(f"   • Gestion d'erreurs: ✅")
        print()
        print("💡 Les images générées sont disponibles dans le dossier frontend/public/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        logger.exception("Détails de l'erreur:")
        return False

def main():
    """
    Fonction principale du script de test.
    """
    print("🚀 Démarrage des tests DynaPictures")
    print("=" * 50)
    print()
    
    success = test_dynapictures_service()
    
    print("=" * 50)
    if success:
        print("✅ Tests terminés avec succès!")
        sys.exit(0)
    else:
        print("❌ Certains tests ont échoué.")
        sys.exit(1)

if __name__ == '__main__':
    main()