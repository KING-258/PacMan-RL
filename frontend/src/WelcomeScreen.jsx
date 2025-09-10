import React, { useState, useEffect } from 'react'

const WelcomeScreen = ({ onStart, layouts, meta, modelInfo }) => {
  const [username, setUsername] = useState('')
  const [layoutName, setLayoutName] = useState('originalClassic')
  const [pacAgent, setPacAgent] = useState('GreedyAgent')
  const [ghostAgent, setGhostAgent] = useState('DirectionalGhost')
  const [modelFile, setModelFile] = useState('')

  // Auto-focus username input on mount
  useEffect(() => {
    const input = document.querySelector('.username-input')
    if (input) input.focus()
  }, [])

  const handleUsernameChange = (e) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3)
    setUsername(value)
  }

  const handleStart = () => {
    if (username.length === 3) {
      onStart({
        username,
        layoutName,
        pacAgent,
        ghostAgent,
        modelFile
      })
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && username.length === 3) {
      handleStart()
    }
  }

  return (
    <div style={{
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontFamily: '"Press Start 2P", monospace'
    }}>
      <div style={{
        background: '#000',
        border: '4px solid #FFD700',
        borderRadius: '20px',
        padding: '40px',
        textAlign: 'center',
        color: '#FFD700',
        boxShadow: '0 0 50px rgba(255, 215, 0, 0.5)',
        minWidth: '500px'
      }}>
        <h1 style={{ 
          fontSize: '36px', 
          marginBottom: '10px',
          textShadow: '2px 2px 4px #ff0000',
          animation: 'pulse 2s infinite'
        }}>
          PAC-MAN
        </h1>
        <h2 style={{ 
          fontSize: '14px', 
          marginBottom: '40px', 
          color: '#00ffff',
          letterSpacing: '2px'
        }}>
          WEB EDITION
        </h2>
        
        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '12px', color: '#fff' }}>
            ENTER YOUR NAME
          </label>
          <input
            type="text"
            value={username}
            onChange={handleUsernameChange}
            onKeyPress={handleKeyPress}
            placeholder="PLAYER 1"
            style={{
              background: '#1a1a1a',
              border: '2px solid #FFD700',
              color: '#FFD700',
              padding: '12px 20px',
              fontSize: '14px',
              fontFamily: 'inherit',
              width: '100%',
              borderRadius: '8px',
              textAlign: 'center',
              outline: 'none'
            }}
            maxLength={20}
          />
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '12px', color: '#fff' }}>
            SELECT LAYOUT
          </label>
          <select
            value={layoutName}
            onChange={(e) => setLayoutName(e.target.value)}
            style={{
              background: '#1a1a1a',
              border: '2px solid #FFD700',
              color: '#FFD700',
              padding: '12px 20px',
              fontSize: '14px',
              fontFamily: 'inherit',
              width: '100%',
              borderRadius: '8px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {layouts.map(name => (
              <option key={name} value={name}>
                {name.replace(/([A-Z])/g, ' $1').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '12px', color: '#fff' }}>
            PAC-MAN AGENT
          </label>
          <select
            value={pacAgent}
            onChange={(e) => setPacAgent(e.target.value)}
            style={{
              background: '#1a1a1a',
              border: '2px solid #FFD700',
              color: '#FFD700',
              padding: '12px 20px',
              fontSize: '14px',
              fontFamily: 'inherit',
              width: '100%',
              borderRadius: '8px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {meta.pacmanAgents?.map(agent => (
              <option key={agent} value={agent}>
                {agent.replace(/([A-Z])/g, ' $1').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '12px', color: '#fff' }}>
            GHOST BEHAVIOR
          </label>
          <select
            value={ghostAgent}
            onChange={(e) => setGhostAgent(e.target.value)}
            style={{
              background: '#1a1a1a',
              border: '2px solid #FFD700',
              color: '#FFD700',
              padding: '12px 20px',
              fontSize: '14px',
              fontFamily: 'inherit',
              width: '100%',
              borderRadius: '8px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {meta.ghostAgents?.map(agent => (
              <option key={agent} value={agent}>
                {agent.replace(/([A-Z])/g, ' $1').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontSize: '12px', color: '#fff' }}>
            AI MODEL
          </label>
          <select
            value={modelFile}
            onChange={(e) => setModelFile(e.target.value)}
            style={{
              background: '#1a1a1a',
              border: '2px solid #FFD700',
              color: '#FFD700',
              padding: '12px 20px',
              fontSize: '12px',
              fontFamily: 'inherit',
              width: '100%',
              borderRadius: '8px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="">MANUAL CONTROL</option>
            {modelInfo.models?.map(model => (
              <option key={model} value={model}>
                {model.replace('.json', '').toUpperCase()}
              </option>
            ))}
          </select>
          <div style={{ marginTop: '10px', fontSize: '10px', color: '#888' }}>
            Select AI model or use manual control
          </div>
        </div>

        <button
          onClick={handleStart}
          disabled={!username.trim()}
          style={{
            background: username.trim() ? 'linear-gradient(145deg, #FFD700, #FFA500)' : '#333',
            border: 'none',
            color: username.trim() ? '#000' : '#666',
            padding: '15px 40px',
            fontSize: '16px',
            fontFamily: 'inherit',
            borderRadius: '8px',
            cursor: username.trim() ? 'pointer' : 'not-allowed',
            fontWeight: 'bold',
            boxShadow: username.trim() ? '0 4px 15px rgba(255, 215, 0, 0.4)' : 'none',
            transition: 'all 0.3s',
            letterSpacing: '2px'
          }}
          onMouseEnter={(e) => {
            if (username.trim()) {
              e.target.style.transform = 'scale(1.05)'
              e.target.style.boxShadow = '0 6px 20px rgba(255, 215, 0, 0.6)'
            }
          }}
          onMouseLeave={(e) => {
            if (username.trim()) {
              e.target.style.transform = 'scale(1)'
              e.target.style.boxShadow = '0 4px 15px rgba(255, 215, 0, 0.4)'
            }
          }}
        >
          START GAME
        </button>

        <div style={{ marginTop: '40px', fontSize: '10px', color: '#666' }}>
          USE ARROW KEYS TO MOVE IN MANUAL MODE
        </div>

        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `}</style>
      </div>
    </div>
  )
}

export default WelcomeScreen
