import React, { useEffect, useState } from 'react'
import { apiLayouts, apiMeta, apiModels } from './api.js'
import WelcomeScreen from './WelcomeScreen.jsx'
import Game from './Game.jsx'

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('loading') 
  const [layouts, setLayouts] = useState([])
  const [meta, setMeta] = useState({ pacmanAgents: [], ghostAgents: [], extractors: [] })
  const [modelInfo, setModelInfo] = useState({ dir: '', models: [] })
  const [gameSettings, setGameSettings] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [layoutsData, metaData, modelData] = await Promise.all([
          apiLayouts(),
          apiMeta(),
          apiModels()
        ])
        
        setLayouts(layoutsData)
        setMeta(metaData)
        setModelInfo(modelData)
        setCurrentScreen('welcome')
      } catch (error) {
        console.error('Failed to load initial data:', error)
        
        setCurrentScreen('welcome')
      } finally {
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [])

  const handleGameStart = (settings) => {
    setGameSettings(settings)
    setCurrentScreen('game')
  }

  const handleBackToWelcome = () => {
    setCurrentScreen('welcome')
    setGameSettings(null)
  }

  if (isLoading || currentScreen === 'loading') {
    return (
      <div className="app-loading">
        <div className="loading-screen">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <div className="loading-text">INITIALIZING PAC-MAN...</div>
            <div className="loading-subtitle">LOADING ARCADE SYSTEMS</div>
          </div>
        </div>
      </div>
    )
  }

  if (currentScreen === 'welcome') {
    return (
      <WelcomeScreen 
        onStart={handleGameStart}
        layouts={layouts}
        meta={meta}
        modelInfo={modelInfo}
      />
    )
  }

  if (currentScreen === 'game' && gameSettings) {
    return (
      <Game 
        gameSettings={gameSettings}
        onBackToWelcome={handleBackToWelcome}
        modelInfo={modelInfo}
      />
    )
  }

  
  return (
    <div className="app-error">
      <div className="error-content">
        <h1>SYSTEM ERROR</h1>
        <p>Failed to initialize Pac-Man arcade system</p>
        <button onClick={() => window.location.reload()}>RESTART</button>
      </div>
    </div>
  )
}

