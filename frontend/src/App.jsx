import { useState, useEffect } from 'react'
import CocktailGenerator from './components/CocktailGenerator'
import CocktailHistory from './components/CocktailHistory'
import CocktailDetail from './components/CocktailDetail'

function App() {
  const [activeTab, setActiveTab] = useState('generator')
  const [selectedCocktail, setSelectedCocktail] = useState(null)
  const [refreshHistory, setRefreshHistory] = useState(0)

  const handleCocktailGenerated = () => {
    setRefreshHistory(prev => prev + 1)
  }

  const handleViewCocktail = (cocktail) => {
    setSelectedCocktail(cocktail)
    setActiveTab('detail')
  }

  return (
    <div className="min-h-screen bg-gray-900">
      

      {/* Navigation */}
      <nav className="border-b border-t border-gold-400/30">
        <div className="container mx-auto px-4">
          <div className="flex justify-center space-x-8">
            <button
              onClick={() => setActiveTab('generator')}
              className={`py-4 px-6 font-medium transition-all duration-300 border-b-2 ${
                activeTab === 'generator'
                  ? 'border-gold-400 text-gold-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              Générateur
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-6 font-medium transition-all duration-300 border-b-2 ${
                activeTab === 'history'
                  ? 'border-gold-400 text-gold-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              Historique
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto">
        {activeTab === 'generator' && (
          <CocktailGenerator onCocktailGenerated={handleCocktailGenerated} />
        )}
        {activeTab === 'history' && (
          <CocktailHistory 
            refreshTrigger={refreshHistory} 
            onViewCocktail={handleViewCocktail}
          />
        )}
        {activeTab === 'detail' && selectedCocktail && (
          <CocktailDetail 
            cocktail={selectedCocktail} 
            onBack={() => setActiveTab('history')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gold-400/30 mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-gray-400">
          <p className="font-modern">
            Copyright © 2024 Le Mixologue Augmenté. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
