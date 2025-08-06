import { useState } from 'react'

const CocktailGenerator = ({ onCocktailGenerated }) => {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [generatedCocktail, setGeneratedCocktail] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) {
      setError('Veuillez saisir une description pour votre cocktail')
      return
    }

    setIsLoading(true)
    setError('')
    setGeneratedCocktail(null)

    try {
      const response = await fetch('http://localhost:5002/api/cocktails/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt.trim() }),
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      if (data.success && data.cocktail) {
        setGeneratedCocktail(data.cocktail)
        setPrompt('')
        onCocktailGenerated?.()
      } else {
        throw new Error('Réponse invalide du serveur')
      }
    } catch (err) {
      console.error('Erreur lors de la génération:', err)
      setError(
        err.message.includes('Failed to fetch')
          ? 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré.'
          : `Erreur lors de la génération: ${err.message}`
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewCocktail = () => {
    setGeneratedCocktail(null)
    setError('')
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card-elegant mb-8">
        <h2 className="text-3xl font-elegant text-gold-400 mb-6 text-center">
          Créer un Nouveau Cocktail
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="prompt" className="block text-lg font-medium text-white mb-3">
              Décrivez le cocktail de vos rêves
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ex: Un cocktail fruité pour une soirée d'été, quelque chose d'épicé pour l'hiver, un drink élégant pour un dîner romantique..."
              className="input-elegant w-full h-32 resize-none"
              disabled={isLoading}
            />
          </div>
          
          {error && (
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
              <p className="text-red-300">{error}</p>
            </div>
          )}
          
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={isLoading || !prompt.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black"></div>
                  <span>Création en cours...</span>
                </>
              ) : (
                <>
                  <span>✨</span>
                  <span>Créer mon cocktail</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Cocktail généré */}
      {generatedCocktail && (
        <div className="card-elegant">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-2xl font-elegant text-gold-400">
              {generatedCocktail.name}
            </h3>
            <button
              onClick={handleNewCocktail}
              className="text-gray-400 hover:text-white transition-colors"
              title="Créer un nouveau cocktail"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">🍸</span>
                Ingrédients
              </h4>
              <ul className="space-y-2">
                {Array.isArray(generatedCocktail.ingredients) ? (
                  generatedCocktail.ingredients.map((ingredient, index) => (
                    <li key={index} className="text-gray-300 flex items-start">
                      <span className="text-gold-400 mr-2">•</span>
                      {ingredient}
                    </li>
                  ))
                ) : (
                  <li className="text-gray-400 italic">
                    Ingrédients non disponibles
                  </li>
                )}
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">📖</span>
                Description
              </h4>
              <p className="text-gray-300 leading-relaxed">
                {generatedCocktail.description}
              </p>
            </div>
          </div>
          
          {generatedCocktail.music_ambiance && (
            <div className="mt-6 pt-6 border-t border-gold-400/30">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">🎵</span>
                Ambiance Musicale
              </h4>
              <p className="text-gray-300 italic">
                {generatedCocktail.music_ambiance}
              </p>
            </div>
          )}
          
          {generatedCocktail.image_prompt && (
            <div className="mt-6 pt-6 border-t border-gold-400/30">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">🎨</span>
                Inspiration Visuelle
              </h4>
              <p className="text-gray-300 text-sm bg-gray-800 p-3 rounded-lg">
                {generatedCocktail.image_prompt}
              </p>
            </div>
          )}
          
          <div className="mt-6 pt-6 border-t border-gold-400/30 text-center">
            <p className="text-gray-400 text-sm">
              Cocktail créé le {new Date(generatedCocktail.created_at).toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default CocktailGenerator