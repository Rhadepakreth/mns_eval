# Intégration Stability AI (SD3) 🎨

## Vue d'ensemble

Cette intégration ajoute le support de **Stability AI v3.5 avec Stable Diffusion 3** comme service prioritaire pour la génération d'images de cocktails, offrant une qualité d'image supérieure par rapport aux solutions locales.

## Architecture des Services d'Image

### Hiérarchie de Priorité
1. **🚀 Stability AI (SD3)** - Service cloud prioritaire (qualité supérieure)
2. **🔄 DynaPictures (Local)** - Service local de fallback
3. **📷 Image par défaut** - Fallback final

### Avantages de Stability AI
- **Qualité supérieure** : Modèle SD3 de dernière génération
- **Rapidité** : Génération cloud optimisée
- **Fiabilité** : Infrastructure professionnelle
- **Résolution** : Images haute définition

## Configuration

### 1. Obtenir une Clé API Stability AI

1. Visitez [platform.stability.ai](https://platform.stability.ai/)
2. Créez un compte ou connectez-vous
3. Naviguez vers la section "API Keys"
4. Générez une nouvelle clé API
5. Copiez la clé (format: `sk-...`)

### 2. Configuration des Variables d'Environnement

```bash
# Dans votre fichier .env
STABILITY_API_KEY=sk-votre_cle_api_ici
```

### 3. Redémarrage du Serveur

```bash
# Arrêter le serveur actuel
pkill -f "python.*app.py"

# Redémarrer avec la nouvelle configuration
PORT=5001 CORS_ORIGINS="http://localhost:5173,http://localhost:5176" python app.py
```

## Fonctionnement

### Logique de Sélection du Service

```python
def generate_image(self, cocktail_data):
    # 1. Essayer Stability AI (prioritaire)
    if self.stability_service and self.stability_service.is_available():
        result = self.stability_service.generate_cocktail_image(cocktail_data)
        if result:
            return result
    
    # 2. Fallback vers DynaPictures (local)
    if self.dynapictures_service:
        result = self.dynapictures_service.generate_cocktail_image(cocktail_data)
        if result:
            return result
    
    # 3. Image par défaut
    return "/default.webp"
```

### Logs de Diagnostic

Le système fournit des logs détaillés pour diagnostiquer l'état des services :

```
✅ Service Stability AI (SD3) initialisé avec succès
⚠️ Service Stability AI disponible mais clé API manquante
🎨 Services d'image disponibles: Stability AI (SD3), DynaPictures (Local)
🚀 Tentative avec Stability AI (SD3)...
✅ Image générée avec Stability AI: /cocktail_123.jpeg
```

## API Stability AI v3.5

### Endpoint Utilisé
```
POST https://api.stability.ai/v2beta/stable-image/generate/sd3
```

### Paramètres de Génération
- **Modèle** : Stable Diffusion 3
- **Format de sortie** : JPEG
- **Résolution** : Optimisée automatiquement
- **Style** : Prompts optimisés pour cocktails

### Exemple de Prompt Généré
```
A professional cocktail photography of [Nom du Cocktail], 
[description des ingrédients], served in [type de verre], 
with [garnitures], professional lighting, high-end bar setting, 
4K quality, food photography style
```

## Gestion des Erreurs

### Cas d'Échec Gérés
1. **Clé API manquante** → Fallback vers DynaPictures
2. **Erreur réseau** → Fallback vers DynaPictures
3. **Quota dépassé** → Fallback vers DynaPictures
4. **Service indisponible** → Fallback vers DynaPictures
5. **Tous les services échouent** → Image par défaut

### Messages d'Erreur Typiques
```
⚠️ STABILITY_API_KEY non définie - service indisponible
⚠️ Échec de génération avec Stability AI, tentative avec DynaPictures...
⚠️ Aucun service de génération disponible, utilisation de l'image par défaut
```

## Tests

### Test de Connectivité
```python
# Le service teste automatiquement la connectivité au démarrage
stability_service = StabilityAIService()
if stability_service.is_available():
    print("✅ Stability AI prêt")
else:
    print("❌ Stability AI indisponible")
```

### Test de Génération
```bash
# Tester via l'API REST
curl -X POST http://localhost:5001/api/cocktails/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Un cocktail tropical rafraîchissant"}'
```

## Coûts et Limites

### Stability AI
- **Coût** : ~$0.04 par image générée
- **Limite de taux** : Selon votre plan d'abonnement
- **Qualité** : Supérieure (SD3)

### DynaPictures (Local)
- **Coût** : Gratuit (utilise les ressources locales)
- **Limite** : Dépend des ressources système
- **Qualité** : Bonne (SD1.5)

## Dépannage

### Problèmes Courants

1. **"Service Stability AI disponible mais clé API manquante"**
   - Vérifiez que `STABILITY_API_KEY` est définie dans `.env`
   - Redémarrez le serveur après modification

2. **"Échec de génération avec Stability AI"**
   - Vérifiez votre quota API
   - Vérifiez la connectivité internet
   - Consultez les logs pour plus de détails

3. **"Aucun service de génération disponible"**
   - Ni Stability AI ni DynaPictures ne sont disponibles
   - Vérifiez les dépendances et la configuration

### Commandes de Diagnostic

```bash
# Vérifier les variables d'environnement
echo $STABILITY_API_KEY

# Vérifier les logs du serveur
tail -f logs/app.log

# Tester la connectivité API
curl -H "Authorization: Bearer $STABILITY_API_KEY" \
     https://api.stability.ai/v1/user/account
```

## Fichiers Modifiés

- `backend/services/stability_ai_service.py` - Nouveau service Stability AI
- `backend/services/mistral_service.py` - Intégration des services d'image
- `backend/.env.example` - Configuration exemple
- `STABILITY_AI_INTEGRATION.md` - Cette documentation

## Prochaines Étapes

1. **Optimisation des prompts** - Améliorer la qualité des descriptions
2. **Cache d'images** - Éviter la régénération d'images identiques
3. **Métriques** - Suivre l'utilisation et les coûts
4. **Interface admin** - Gérer les services depuis l'interface

---

**Note** : Cette intégration maintient une compatibilité totale avec l'existant. Si Stability AI n'est pas configuré, le système utilise automatiquement DynaPictures comme avant.