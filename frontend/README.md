# Le Mixologue Augmenté - Frontend

Application React élégante pour créer des cocktails personnalisés avec l'intelligence artificielle.

## 🎨 Design

L'application présente un design sophistiqué avec :
- **Fond noir** pour une ambiance premium
- **Bordures dorées** pour l'élégance
- **Texte blanc** pour la lisibilité
- **Police Playfair Display** pour les titres (élégante)
- **Police Inter** pour le contenu (moderne et lisible)

## ✨ Fonctionnalités

### 🍸 Générateur de Cocktails
- Interface intuitive pour décrire le cocktail souhaité
- Génération en temps réel via l'API Mistral
- Affichage complet des résultats :
  - Nom créatif du cocktail
  - Liste détaillée des ingrédients
  - Description narrative
  - Suggestion d'ambiance musicale
  - Prompt pour génération d'image

### 📚 Historique des Cocktails
- Grille élégante des cocktails créés
- Pagination automatique
- Aperçu rapide avec ingrédients principaux
- Navigation fluide vers les détails

### 🔍 Détails des Cocktails
- Vue complète d'un cocktail sélectionné
- Fonctions de copie (ingrédients, recette complète)
- Affichage de la demande originale
- Interface responsive et accessible

## 🚀 Installation et Démarrage

### Prérequis
- Node.js 18+
- npm ou yarn
- Backend "Le Mixologue Augmenté" en cours d'exécution

### Installation
```bash
# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

### Configuration

L'application se connecte automatiquement au backend sur `http://localhost:5002`.

Si votre backend utilise un port différent, modifiez les URLs dans :
- `src/components/CocktailGenerator.jsx`
- `src/components/CocktailHistory.jsx`

## 🛠️ Technologies Utilisées

- **React 18** - Framework frontend
- **Vite** - Outil de build rapide
- **Tailwind CSS** - Framework CSS utilitaire
- **Google Fonts** - Polices Playfair Display & Inter

## 📱 Responsive Design

L'application s'adapte automatiquement à tous les écrans :
- **Desktop** : Grille 3 colonnes pour l'historique
- **Tablet** : Grille 2 colonnes
- **Mobile** : Colonne unique avec navigation optimisée

## 🎯 Utilisation

1. **Créer un cocktail** :
   - Aller dans l'onglet "Générateur"
   - Décrire le cocktail souhaité (ex: "Un cocktail fruité pour l'été")
   - Cliquer sur "Créer mon cocktail"
   - Admirer le résultat généré par l'IA !

2. **Consulter l'historique** :
   - Aller dans l'onglet "Historique"
   - Parcourir les cocktails créés
   - Cliquer sur un cocktail pour voir les détails

3. **Fonctions avancées** :
   - Copier les ingrédients individuellement
   - Copier la recette complète
   - Voir le prompt de génération d'image

## 🎨 Personnalisation

### Couleurs
Les couleurs sont définies dans `tailwind.config.js` :
```javascript
colors: {
  gold: {
    400: '#fbbf24',
    500: '#f59e0b', 
    600: '#d97706',
  }
}
```

### Composants CSS
Classes utilitaires personnalisées dans `src/index.css` :
- `.btn-primary` - Boutons dorés avec gradient
- `.card-elegant` - Cartes avec bordures dorées
- `.input-elegant` - Champs de saisie stylisés

## 🔧 Scripts Disponibles

```bash
# Développement
npm run dev

# Build de production
npm run build

# Aperçu du build
npm run preview

# Linting
npm run lint
```

## 🌟 Fonctionnalités Avancées

- **Gestion d'erreurs** complète avec messages utilisateur
- **États de chargement** avec spinners élégants
- **Animations fluides** avec Tailwind CSS
- **Accessibilité** optimisée (ARIA, navigation clavier)
- **Performance** optimisée avec Vite et React

## 🎭 Expérience Utilisateur

- **Feedback visuel** immédiat sur toutes les actions
- **Navigation intuitive** entre les sections
- **Responsive design** pour tous les appareils
- **Animations subtiles** pour une expérience premium
- **Gestion d'erreurs** avec messages clairs

---

*Créé avec ❤️ et ✨ pour une expérience de mixologie augmentée*

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
