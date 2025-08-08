# Guide d'utilisation - Stable Diffusion v1.5

## 🎨 Migration de DynaPictures vers Stable Diffusion

Ce guide explique comment utiliser la nouvelle implémentation de génération d'images basée sur **Stable Diffusion v1.5** qui remplace l'ancien service DynaPictures.

## 📋 Prérequis

### 1. Compte Hugging Face
- Créez un compte sur [Hugging Face](https://huggingface.co/)
- Générez un token d'accès sur [Settings > Tokens](https://huggingface.co/settings/tokens)
- Le modèle `runwayml/stable-diffusion-v1-5` est libre d'accès
- Aucune demande d'autorisation nécessaire

### 2. Configuration système
- **Python 3.8+** (testé avec Python 3.13)
- **8GB+ de RAM** recommandés
- **GPU CUDA** (optionnel mais fortement recommandé pour de meilleures performances)
- **Espace disque**: ~5GB pour le modèle et les dépendances

## 🚀 Installation et Configuration

### 1. Installation des dépendances

```bash
cd backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration du token Hugging Face

Modifiez le fichier `backend/.env` :

```env
# Configuration Hugging Face pour Stable Diffusion
HUGGINGFACE_TOKEN=hf_votre_token_ici
```

**⚠️ Important**: Remplacez `<VOTRE-TOKEN-HUGGINGFACE>` par votre vrai token.

### 3. Démarrage du serveur

```bash
cd backend
source venv/bin/activate
python app.py
```

## 🎯 Fonctionnalités

### Génération d'images automatique
- **Depuis le générateur**: L'image est générée automatiquement lors de la création d'un nouveau cocktail
- **Depuis l'historique**: L'image existante est récupérée depuis la base de données
- **Prompts intelligents**: Construction automatique de prompts basés sur les ingrédients et descriptions

### Optimisations incluses
- **Détection automatique GPU/CPU**: Utilise CUDA si disponible, sinon CPU
- **Optimisations mémoire**: `enable_model_cpu_offload()` et `enable_attention_slicing()`
- **Haute qualité**: Images 1024x1024 avec 50 étapes d'inférence
- **Sauvegarde optimisée**: Format PNG avec compression

## 🔧 Paramètres de génération

### Paramètres par défaut
```python
generation_params = {
    "num_inference_steps": 50,    # Qualité élevée
    "guidance_scale": 7.5,        # Équilibre créativité/fidélité
    "width": 1024,                # Haute résolution
    "height": 1024
}
```

### Construction de prompts
Le système construit automatiquement des prompts optimisés :

1. **Utilise le prompt personnalisé** si `image_prompt` est fourni
2. **Sinon, construit automatiquement** basé sur :
   - Nom du cocktail
   - Ingrédients (avec mapping de couleurs)
   - Description (avec indices de style)
   - Qualificatifs professionnels

### Exemple de prompt généré
```
A beautiful Mojito Tropical cocktail in an elegant glass, 
with golden amber, bright yellow tones, 
tropical paradise setting with palm leaves, 
professional photography, high quality, detailed, 8k resolution, 
studio lighting, elegant presentation, premium cocktail, 
sophisticated bar setting, crystal clear glass
```

## 🎨 Personnalisation des prompts

### Dans l'interface utilisateur
Lors de la génération d'un cocktail, vous pouvez fournir un `image_prompt` personnalisé qui sera utilisé comme base pour la génération.

### Mapping des couleurs
Le système reconnaît automatiquement les ingrédients et applique des couleurs appropriées :

```python
color_map = {
    'rhum': 'golden amber',
    'whisky': 'deep amber',
    'vodka': 'crystal clear',
    'gin': 'clear with botanical hints',
    'tequila': 'pale gold',
    'grenadine': 'ruby red gradient',
    # ... etc
}
```

### Styles automatiques
Détection de mots-clés pour appliquer des styles :

```python
style_keywords = {
    'tropical': 'tropical paradise setting with palm leaves',
    'summer': 'bright summer atmosphere',
    'winter': 'cozy winter ambiance',
    'elegant': 'sophisticated upscale bar',
    # ... etc
}
```

## 🔍 Diagnostic et dépannage

### Vérification de l'installation
Le système inclut des tests automatiques pour vérifier :
- ✅ Authentification Hugging Face
- ✅ Disponibilité CUDA/CPU
- ✅ Chargement du modèle
- ✅ Génération de test

### Messages d'erreur courants

#### Token Hugging Face manquant
```
HUGGINGFACE_TOKEN non configuré. 
Veuillez définir cette variable d'environnement...
```
**Solution**: Configurez votre token dans le fichier `.env`

#### Premier téléchargement du modèle
```
Téléchargement en cours... (~5GB)
```
- **Normal** : Le premier démarrage télécharge le modèle complet
- **Durée** : 10-30 minutes selon votre connexion
- **Emplacement** : `~/.cache/huggingface/transformers/`
- **Une seule fois** : Les démarrages suivants seront rapides

#### Modèle non accessible
```
Authentification Hugging Face échouée
```
**Solution**: Vérifiez que votre token a accès au modèle `stabilityai/stable-diffusion-3.5-large`

#### Mémoire insuffisante
```
CUDA out of memory
```
**Solution**: Le système basculera automatiquement sur CPU ou réduisez la résolution

### Logs de diagnostic
Les logs incluent des émojis pour faciliter le diagnostic :
- 🔄 Initialisation en cours
- ✅ Opération réussie
- ❌ Erreur
- ⚠️ Avertissement
- 🎨 Génération d'image
- 💾 Sauvegarde

## 📊 Performance

### Temps de génération estimés
- **GPU CUDA**: 30-60 secondes
- **CPU**: 5-15 minutes
- **Première génération**: Plus lent (chargement du modèle)

### Optimisations recommandées
1. **Utilisez un GPU CUDA** si possible
2. **Gardez le serveur actif** pour éviter le rechargement du modèle
3. **Surveillez la mémoire** (le modèle fait ~6GB)

## 🔄 Migration depuis DynaPictures

### Changements principaux
1. **Service remplacé**: `DynaPicturesService` utilise maintenant Stable Diffusion
2. **Configuration**: `HUGGINGFACE_TOKEN` au lieu de `DYNAPICTURES_API_KEY`
3. **Génération locale**: Plus de dépendance à une API externe
4. **Qualité supérieure**: Images 1024x1024 vs templates fixes

### Compatibilité
- ✅ **Interface identique**: Aucun changement côté frontend
- ✅ **API compatible**: Mêmes endpoints et réponses
- ✅ **Base de données**: Aucune migration nécessaire

## 🛡️ Sécurité

### Bonnes pratiques
1. **Token sécurisé**: Ne commitez jamais votre token Hugging Face
2. **Environnement isolé**: Utilisez un environnement virtuel
3. **Accès modèle**: Vérifiez les permissions d'accès au modèle

### Variables d'environnement
```env
# ✅ Correct
HUGGINGFACE_TOKEN=hf_votre_token_ici

# ❌ À éviter
HUGGINGFACE_TOKEN=<VOTRE-TOKEN-HUGGINGFACE>
```

## 📈 Monitoring

### Informations système
Utilisez `get_service_info()` pour obtenir :
```python
{
    "service_name": "Stable Diffusion 3.5 Large",
    "model_id": "stabilityai/stable-diffusion-3.5-large",
    "device": "cuda",  # ou "cpu"
    "cuda_available": true,
    "pipeline_loaded": true,
    "hf_authenticated": true
}
```

### Test de connexion
```python
service = DynaPicturesService()
success = service.test_connection()
```

## 🎉 Avantages de Stable Diffusion

### Par rapport à DynaPictures
1. **🎨 Créativité illimitée**: Génération basée sur IA vs templates fixes
2. **🏠 Hébergement local**: Pas de dépendance externe
3. **💰 Coût réduit**: Pas de frais par génération
4. **🔧 Contrôle total**: Personnalisation complète des prompts
5. **📈 Qualité supérieure**: Images haute résolution et détaillées
6. **🚀 Évolutivité**: Possibilité d'utiliser d'autres modèles

### Flexibilité
- **Prompts personnalisés**: Contrôle total sur le style
- **Paramètres ajustables**: Qualité, résolution, style
- **Extensions possibles**: Intégration d'autres modèles Diffusion

---

## 🆘 Support

Pour toute question ou problème :
1. Vérifiez les logs du serveur
2. Consultez la documentation Hugging Face
3. Testez avec `test_connection()`

**Bonne génération d'images ! 🎨✨**