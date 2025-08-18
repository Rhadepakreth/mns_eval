#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct du scheduler EulerDiscreteScheduler pour vérifier la stabilité
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.dynapictures_service import DynaPicturesService
import time

def test_direct_generation():
    """
    Test direct de génération d'image avec le nouveau scheduler
    """
    print("🚀 Test direct du scheduler EulerDiscreteScheduler")
    print("=" * 50)
    
    try:
        # Initialiser le service
        print("📦 Initialisation du service DynaPictures...")
        service = DynaPicturesService()
        
        if not service.is_available():
            print("❌ Service DynaPictures non disponible")
            return False
            
        print("✅ Service DynaPictures initialisé")
        
        # Test avec un prompt simple
        simple_prompt = "A colorful cocktail in a glass"
        print(f"🎨 Test avec prompt simple: {simple_prompt}")
        
        start_time = time.time()
        result = service.generate_image(simple_prompt)
        end_time = time.time()
        
        if result:
            print(f"✅ Image générée avec succès: {result}")
            print(f"⏱️ Temps de génération: {end_time - start_time:.2f} secondes")
            return True
        else:
            print("❌ Échec de génération d'image")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_generation()
    if success:
        print("\n🎉 Test réussi ! Le scheduler EulerDiscreteScheduler fonctionne")
    else:
        print("\n❌ Test échoué ! Problème avec le scheduler")
    
    sys.exit(0 if success else 1)