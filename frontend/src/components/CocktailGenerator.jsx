import { useState } from 'react'
import CocktailDetail from './CocktailDetail'

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
      
        {/* Header */}
      <header>
        <div className="container mx-auto px-4 py-4">
          
          <h1 className="text-[clamp(6rem,13vw,14rem)] font-elegant text-white yesteryear-regular">
            <span className="block text-center">
              <span className="relative inline-block transform -translate-x-10">
                <span className="text-[clamp(2rem,5vw,6rem)] mr-2 inline-block transform -translate-y-8">Le </span>Mixologue
              </span>
              <span className="block transform -translate-y-[8.5vw] translate-x-[8.5vw] text-[clamp(4rem,9vw,8rem)]">🍸Augmenté</span>
            </span>
          </h1>
          <p className="text-center text-gold-400 text-[clamp(0.8rem,1.7vw,1.5rem)] font-modern -mt-[10vw]">
            Créez des cocktails uniques avec l'intelligence artificielle
          </p>
          
        </div>
      </header>
      <div className="">
        <div className="card-elegant mb-8 w-2/3 mx-auto">
          <h2 className="text-3xl font-elegant text-white mb-6 text-center">
            Créer un Nouveau Cocktail
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="prompt" className="block text-lg font-medium text-gold-400 mb-3">
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
      </div>

      {/* Cocktail généré */}
      {generatedCocktail && (
        <CocktailDetail 
          cocktail={generatedCocktail} 
          onBack={handleNewCocktail}
          source="generator"
        />
      )}
    </div>
  )
}

export default CocktailGenerator