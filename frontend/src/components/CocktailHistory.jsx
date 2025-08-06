import { useState, useEffect } from 'react'

const CocktailHistory = ({ refreshTrigger, onViewCocktail }) => {
  const [cocktails, setCocktails] = useState([])
  const [pagination, setPagination] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [perPage] = useState(6)
  const [deletingId, setDeletingId] = useState(null)

  const fetchCocktails = async (page = 1) => {
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(
        `http://localhost:5002/api/cocktails?page=${page}&per_page=${perPage}`
      )

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setCocktails(data.cocktails || [])
      setPagination(data.pagination)
      setCurrentPage(page)
    } catch (err) {
      console.error('Erreur lors du chargement:', err)
      setError(
        err.message.includes('Failed to fetch')
          ? 'Impossible de se connecter au serveur. Vérifiez que le backend est démarré.'
          : `Erreur lors du chargement: ${err.message}`
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCocktails(1)
  }, [refreshTrigger])

  const handlePageChange = (page) => {
    fetchCocktails(page)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const deleteCocktail = async (cocktailId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce cocktail ?')) {
      return
    }

    setDeletingId(cocktailId)
    try {
      const response = await fetch(`http://localhost:5002/api/cocktails/${cocktailId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()

      if (data.success) {
        // Supprimer le cocktail de la liste locale
        setCocktails(prevCocktails => prevCocktails.filter(c => c.id !== cocktailId))
        // Recharger la page si nécessaire
        if (cocktails.length === 1 && currentPage > 1) {
          fetchCocktails(currentPage - 1)
        }
      } else {
        setError(data.error || 'Erreur lors de la suppression')
      }
    } catch (err) {
      console.error('Erreur lors de la suppression:', err)
      setError('Erreur de connexion lors de la suppression')
    } finally {
      setDeletingId(null)
    }
  }

  if (isLoading && cocktails.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card-elegant text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gold-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Chargement de l'historique...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card-elegant">
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-6 text-center">
            <h3 className="text-xl font-semibold text-red-300 mb-2">Erreur</h3>
            <p className="text-red-300 mb-4">{error}</p>
            <button
              onClick={() => fetchCocktails(currentPage)}
              className="btn-primary"
            >
              Réessayer
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (cocktails.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="card-elegant text-center">
          <div className="text-6xl mb-4">🍸</div>
          <h3 className="text-2xl font-elegant text-gold-400 mb-2">
            Aucun cocktail créé
          </h3>
          <p className="text-gray-300 mb-6">
            Commencez par créer votre premier cocktail dans l'onglet Générateur !
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-4 mt-4">
        <h2 className="text-3xl font-elegant text-gold-400 text-center mb-2">
          Historique des Cocktails
        </h2>
        <p className="text-center text-gray-300">
          {pagination?.total || 0} cocktail{(pagination?.total || 0) > 1 ? 's' : ''} créé{(pagination?.total || 0) > 1 ? 's' : ''}
        </p>
      </div>

      {/* Grille des cocktails */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-4">
        {cocktails.map((cocktail) => (
          <div key={cocktail.id} className="card-elegant hover:border-gold-300 transition-all duration-300 cursor-pointer group"
               onClick={() => onViewCocktail(cocktail)}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-elegant text-gold-400 group-hover:text-gold-300 transition-colors">
                {cocktail.name}
              </h3>
              <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
                #{cocktail.id}
              </span>
            </div>
            
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-white mb-2 flex items-center">
                <span className="mr-2">🍸</span>
                Ingrédients ({Array.isArray(cocktail.ingredients) ? cocktail.ingredients.length : 0})
              </h4>
              <div className="text-sm text-gray-300 space-y-1">
                {Array.isArray(cocktail.ingredients) ? (
                  cocktail.ingredients.slice(0, 2).map((ingredient, index) => (
                    <div key={index} className="flex items-start">
                      <span className="text-gold-400 mr-2 text-xs">•</span>
                      <span className="truncate">{ingredient}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-gray-400 italic">
                    Ingrédients non disponibles
                  </div>
                )}
                {Array.isArray(cocktail.ingredients) && cocktail.ingredients.length > 3 && (
                  <div className="text-xs text-gray-400 italic">
                    +{cocktail.ingredients.length - 2} autre{cocktail.ingredients.length - 2 > 1 ? 's' : ''} ingrédient{cocktail.ingredients.length - 2 > 1 ? 's' : ''}...
                  </div>
                )}
              </div>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-300 line-clamp-2">
                {cocktail.description}
              </p>
            </div>
            
            <div className="flex justify-between items-center pt-4 border-t border-gold-400/30">
              <span className="text-xs text-gray-400">
                {formatDate(cocktail.created_at)}
              </span>
              <div className="flex items-center gap-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteCocktail(cocktail.id)
                  }}
                  disabled={deletingId === cocktail.id}
                  className="flex items-center text-red-400 hover:text-red-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Supprimer ce cocktail"
                >
                  {deletingId === cocktail.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-400"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  )}
                </button>
                <div className="flex items-center text-gold-400 group-hover:text-gold-300 transition-colors">
                  <span className="text-sm mr-1">Voir détails</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination && pagination.pages > 1 && (
        <div className="flex justify-center items-center space-x-4">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={!pagination.has_prev || isLoading}
            className="px-4 py-2 border border-gold-400 text-gold-400 rounded-lg hover:bg-gold-400 hover:text-black transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Précédent
          </button>
          
          <div className="flex space-x-2">
            {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                disabled={isLoading}
                className={`px-3 py-2 rounded-lg transition-all duration-300 ${
                  page === currentPage
                    ? 'bg-gold-400 text-black'
                    : 'border border-gold-400 text-gold-400 hover:bg-gold-400 hover:text-black'
                } disabled:opacity-50`}
              >
                {page}
              </button>
            ))}
          </div>
          
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={!pagination.has_next || isLoading}
            className="px-4 py-2 border border-gold-400 text-gold-400 rounded-lg hover:bg-gold-400 hover:text-black transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Suivant
          </button>
        </div>
      )}
      
      {isLoading && (
        <div className="text-center mt-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-400 mx-auto"></div>
        </div>
      )}
    </div>
  )
}

export default CocktailHistory