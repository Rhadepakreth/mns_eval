# Guide de Sécurité - Le Mixologue Augmenté

## 🔒 Mesures de Sécurité Implémentées

### 1. Configuration Sécurisée

#### Variables d'Environnement
- **SECRET_KEY** : Génération automatique sécurisée si non définie
- **CORS_ORIGINS** : Validation stricte des origines autorisées
- **DATABASE_URL** : Configuration sécurisée de la base de données
- Logging sécurisé avec rotation des fichiers

#### Headers de Sécurité
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy: default-src 'self'`
- `Strict-Transport-Security` (HTTPS uniquement)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 2. Validation et Sanitisation des Entrées

#### Validation des Prompts
- Échappement HTML automatique
- Nettoyage avec la bibliothèque `bleach`
- Validation de longueur (10-1000 caractères)
- Blocage des caractères dangereux (`<`, `>`, `script`, etc.)

#### Validation des Paramètres
- **IDs de cocktail** : Validation d'entiers positifs
- **Pagination** : Limites strictes (page ≥ 1, per_page ≤ 50)
- **Noms de fichiers** : Protection contre la traversée de répertoire

### 3. Rate Limiting

| Endpoint | Limite | Fenêtre |
|----------|--------|----------|
| `/api/cocktails/generate` | 5 requêtes | 60 secondes |
| `/api/cocktails` | 20 requêtes | 60 secondes |
| `/api/cocktails/<id>` | 30 requêtes | 60 secondes |
| `/api/cocktails/<id>` (DELETE) | 10 requêtes | 60 secondes |
| `/api/cocktails/generate-image` | 3 requêtes | 60 secondes |
| Fichiers statiques | 50 requêtes | 60 secondes |

### 4. Protection des Fichiers

#### Extensions Autorisées
- Images : `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`
- Blocage de toutes les autres extensions

#### Protection contre la Traversée de Répertoire
- Validation stricte des chemins de fichiers
- Blocage des caractères `..`, `/`, `\\`
- Logging des tentatives d'attaque

### 5. Gestion des Erreurs

#### Gestionnaires Sécurisés
- **404** : Endpoint non trouvé (avec logging)
- **400** : Requête invalide
- **403** : Accès interdit
- **429** : Limite de taux dépassée
- **500** : Erreur interne (sans révélation d'informations)

#### Logging de Sécurité
- Événements de sécurité tracés avec horodatage
- Types d'événements : `INVALID_REQUEST`, `INVALID_INPUT`, `PATH_TRAVERSAL_ATTEMPT`, etc.
- Rotation automatique des logs

### 6. Base de Données

#### Configuration Sécurisée
- Pool de connexions avec `pool_pre_ping`
- Recyclage des connexions (`pool_recycle: 300s`)
- Protection contre l'injection SQL via SQLAlchemy ORM

## 🚀 Déploiement en Production

### Variables d'Environnement Obligatoires

```bash
# Générer une clé secrète sécurisée
python -c "import secrets; print(secrets.token_hex(32))"

# Configuration production
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre_cle_secrete_generee
CORS_ORIGINS=https://votre-domaine.com
DATABASE_URL=postgresql://user:pass@host:port/db
MISTRAL_API_KEY=votre_cle_mistral
```

### Recommandations Additionnelles

1. **HTTPS Obligatoire** : Utilisez un certificat SSL/TLS
2. **Reverse Proxy** : Nginx ou Apache devant Flask
3. **Firewall** : Limitez l'accès aux ports nécessaires
4. **Monitoring** : Surveillez les logs de sécurité
5. **Mises à jour** : Maintenez les dépendances à jour

### Commandes de Vérification

```bash
# Test de santé
curl -X GET https://votre-domaine.com/health

# Test de rate limiting
for i in {1..10}; do curl -X POST https://votre-domaine.com/api/cocktails/generate; done

# Test de sécurité des fichiers
curl -X GET https://votre-domaine.com/../../../etc/passwd
```

## 🔍 Audit de Sécurité

### Vulnérabilités Corrigées

✅ **Injection XSS** : Sanitisation des entrées utilisateur  
✅ **Traversée de répertoire** : Validation des chemins de fichiers  
✅ **Déni de service** : Rate limiting implémenté  
✅ **Headers manquants** : Headers de sécurité ajoutés  
✅ **Configuration faible** : Clés secrètes et CORS sécurisés  
✅ **Gestion d'erreurs** : Pas de révélation d'informations sensibles  
✅ **Logging insuffisant** : Événements de sécurité tracés  

### Tests de Sécurité Réalisés

- ✅ Validation des entrées (XSS, injection)
- ✅ Rate limiting fonctionnel
- ✅ Protection des fichiers statiques
- ✅ Headers de sécurité présents
- ✅ Gestion d'erreurs sécurisée
- ✅ Configuration robuste

## 📞 Support

Pour toute question de sécurité, consultez les logs de l'application ou contactez l'équipe de développement.

---

**Dernière mise à jour** : 18 août 2025  
**Version** : 1.0.0  
**Statut** : Production Ready 🚀