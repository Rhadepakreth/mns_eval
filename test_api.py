#!/usr/bin/env python3
import requests
import json

def test_cocktail_generation():
    url = 'http://localhost:5002/api/cocktails/generate'
    data = {'prompt': 'Un cocktail fruité pour tester'}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            cocktail = response.json()['cocktail']
            print(f"\nIngrédients type: {type(cocktail['ingredients'])}")
            print(f"Ingrédients: {cocktail['ingredients']}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    test_cocktail_generation()