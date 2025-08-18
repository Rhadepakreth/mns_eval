import { useState, useEffect } from 'react'

const CocktailDetail = ({ cocktail, onBack, source = 'history' }) => {
  const [generatedImage, setGeneratedImage] = useState(null)
  const [isGeneratingImage, setIsGeneratingImage] = useState(false)
  const [imageError, setImageError] = useState(null)
  const [showDefaultImage, setShowDefaultImage] = useState(false)

  // Gérer l'affichage de l'image au chargement
  useEffect(() => {
    // Si une image est déjà générée et stockée, l'utiliser
    if (cocktail.image_path) {
      setGeneratedImage(cocktail.image_path)
      setShowDefaultImage(false)
    } else if (source === 'generator' && cocktail.image_prompt && !generatedImage) {
      // Générer automatiquement l'image seulement si appelé depuis le générateur
      generateImage()
    } else {
      // Si appelé depuis l'historique ou pas de prompt, afficher l'image par défaut
      setShowDefaultImage(true)
    }
  }, [cocktail.id, cocktail.image_path, source])

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Vous pourriez ajouter une notification ici
    })
  }

  const generateImage = async () => {
    if (!cocktail.id) return
    
    setIsGeneratingImage(true)
    setImageError(null)
    
    try {
      const response = await fetch('http://localhost:5001/api/cocktails/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cocktail_id: cocktail.id
        })
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors de la génération de l\'image')
      }
      
      const data = await response.json()
      
      if (data.image_url) {
        setGeneratedImage(data.image_url)
        setShowDefaultImage(false)
        
        // Mettre à jour le cocktail local avec le chemin de l'image
        cocktail.image_path = data.image_url
      } else {
        setImageError('Génération d\'images temporairement indisponible. Le service DynaPictures n\'est pas configuré.')
        setShowDefaultImage(true)
      }
    } catch (error) {
      console.error('Erreur génération image:', error)
      if (error.message.includes('500')) {
        setImageError('Service de génération d\'images temporairement indisponible')
      } else {
        setImageError('Erreur lors de la génération de l\'image')
      }
      setShowDefaultImage(true)
    } finally {
      setIsGeneratingImage(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header avec bouton retour */}
      <div className="flex items-center mb-4 mt-4">
        <button
          onClick={onBack}
          className="flex items-center text-gold-400 hover:text-gold-300 transition-colors mr-4"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Retour à l'historique
        </button>
        <div className="h-px bg-gold-400/30 flex-1"></div>
      </div>

      {/* Carte principale du cocktail */}
      <div className="card-elegant mb-8">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-6xl yesteryear-regular text-white">
              {cocktail.name}
            </h1>
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <span>Créé le {formatDate(cocktail.created_at)}</span>
            </div>
          </div>
          <div className="text-right text-gold-400">
            <span>Cocktail #{cocktail.id}</span>
          </div>
        </div>

        

            {/* Description */}
            <div className="my-4">
              <h3 className="text-2xl font-elegant text-gold-400 mb-2 flex items-center">
                Description
              </h3>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed text-lg">
                  {cocktail.description}
                </p>
              </div>
            </div>

        {/* Grille principale */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Colonne gauche : Demande originale et Image */}
          <div className="space-y-6">
            {/* Indicateur de génération d'image */}
            {isGeneratingImage && (
              <div className="rounded-lg border border-gold-400/30 text-center flex-1 w-full h-full min-h-[400px]">
                <div className="flex items-center justify-center w-full h-full space-x-3">
                  <svg className="animate-spin w-6 h-6 text-gold-400" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-gold-400">Génération de l'image en cours...</span>
                </div>
              </div>
            )}
            {/* Image du cocktail */}
            {(generatedImage || showDefaultImage) && (
              <div className="flex-1">
                <img 
                  src={generatedImage || '/default.webp'} 
                  alt={generatedImage ? `Illustration du cocktail ${cocktail.name}` : 'Image par défaut de cocktail'}
                  className="w-full h-full min-h-[400px] object-cover rounded-lg border border-gold-400/30 shadow-lg"
                  onError={() => setImageError('Erreur lors du chargement de l\'image')}
                />
                {showDefaultImage && !generatedImage}
              </div>
            )}
          </div>

          {/* Colonne droite : Ingrédients */}
          <div>
            <h3 className="text-2xl font-elegant text-gold-400 mb-4 flex items-center">
              Ingrédients
              {/* Bouton copier tous les ingrédients */}
            {Array.isArray(cocktail.ingredients) && (
              <button
                onClick={() => copyToClipboard(cocktail.ingredients.join('\n'))}
                className=" ml-auto text-sm text-gold-400 hover:text-gold-300 transition-colors flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            )}
            </h3>
            <div className="space-y-3">
              {Array.isArray(cocktail.ingredients) ? (
                cocktail.ingredients.map((ingredient, index) => (
                  <div key={index} className="flex items-start group">
                    <span className="w-2 h-2 bg-white/50 mt-2 mr-2 rotate-45"></span>
                    <span className="text-gray-300 flex-1">{ingredient}</span>
                    <button
                      onClick={() => copyToClipboard(ingredient)}
                      className="opacity-0 group-hover:opacity-100 ml-2 text-gray-400 hover:text-gold-400 transition-all duration-200"
                      title="Copier l'ingrédient"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-400 italic">
                    Ingrédients non disponibles
                  </div>
                )}
            </div>            
          </div>
          {/* Demande originale */}
            {cocktail.user_prompt && (
              <div className="p-4 bg-gray-300/10 rounded-lg border-l-4 border-gold-400">
                <h3 className="text-lg font-semibold text-white mb-2 flex items-center">
                  Demande originale
                </h3>
                <p className="text-gray-300 italic">
                  "{cocktail.user_prompt}"
                </p>
              </div>
            )}
        {/* Ambiance musicale */}
            {cocktail.music_ambiance && (
              <div className=" card-elegant">
                <h3 className="text-2xl font-elegant text-gold-400 mb-4 flex items-center">
                  Ambiance Musicale
                </h3>
                <p className="text-gray-300 italic leading-relaxed">
                  {cocktail.music_ambiance}
                </p>
              </div>
            )}
        </div>
      </div>

    </div>
  )
}

export default CocktailDetail