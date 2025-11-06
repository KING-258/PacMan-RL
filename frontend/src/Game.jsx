import React, { useEffect, useMemo, useRef, useState } from 'react'
import { apiReset, apiStep } from './api.js'

const WALL_COLOR = '#1f51ff'
const FOOD_COLOR = '#f7f7f7'
const CAPSULE_COLOR = '#ffffff'
const PAC_COLOR = '#ffcc00'
const GHOST_COLORS = ['#ff3a3a', '#4d83ff', '#fa9412', '#18bfae']

function useAnimationLoop(enabled, tick, speed) {
  useEffect(() => {
    if (!enabled) return
    let raf
    let last = performance.now()
    const speedMap = { 1: 200, 2: 100, 3: 50, 4: 25, 5: 10 }
    const interval = speedMap[speed] || 100
    
    const loop = (t) => {
      if (t - last > interval) {
        last = t
        tick()
      }
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(raf)
  }, [enabled, tick, speed])
}

function drawPacman(ctx, x, y, r, dirRad) {
  
  const mouth = Math.PI / 6
  ctx.fillStyle = PAC_COLOR
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.arc(x, y, r, mouth + dirRad, 2 * Math.PI - mouth + dirRad)
  ctx.closePath()
  ctx.fill()
}

function drawGhost(ctx, x, y, r, color, scared=false) {
  ctx.fillStyle = scared ? '#2bbcdc' : color
  
  ctx.beginPath()
  ctx.arc(x, y - r * 0.2, r, Math.PI, 0)
  ctx.lineTo(x + r, y + r * 0.6)
  
  const bumps = 4
  for (let i = bumps; i >= 0; i--) {
    const bx = x - r + (2 * r * i) / bumps
    const by = y + r * 0.6
    ctx.quadraticCurveTo(bx - r / bumps / 2, by + r * 0.35, bx, by)
  }
  ctx.closePath()
  ctx.fill()
  
  ctx.fillStyle = '#ffffff'
  const exOff = r * 0.35
  const eyOff = r * -0.2
  const er = r * 0.35
  ctx.beginPath(); ctx.arc(x - exOff, y + eyOff, er, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(x + exOff, y + eyOff, er, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = '#1f3bff'
  const pr = er * 0.5
  ctx.beginPath(); ctx.arc(x - exOff + pr * 0.5, y + eyOff, pr, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(x + exOff + pr * 0.5, y + eyOff, pr, 0, Math.PI * 2); ctx.fill()
}

function drawState(ctx, state, scale) {
  const w = state.width
  const h = state.height
  ctx.clearRect(0, 0, w * scale, h * scale)

  
  ctx.fillStyle = WALL_COLOR
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) {
      if (state.walls[x][y]) {
        ctx.fillRect(x * scale, (h - 1 - y) * scale, scale, scale)
      }
    }
  }

  
  ctx.fillStyle = FOOD_COLOR
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) {
      if (state.food[x][y]) {
        const cx = x * scale + scale / 2
        const cy = (h - 1 - y) * scale + scale / 2
        ctx.beginPath()
        ctx.arc(cx, cy, Math.max(1, scale * 0.12), 0, Math.PI * 2)
        ctx.fill()
      }
    }
  }

  
  ctx.fillStyle = CAPSULE_COLOR
  state.capsules.forEach(([x, y]) => {
    const cx = x * scale + scale / 2
    const cy = (h - 1 - y) * scale + scale / 2
    ctx.beginPath()
    ctx.arc(cx, cy, Math.max(2, scale * 0.25), 0, Math.PI * 2)
    ctx.fill()
  })

  
  const [px, py] = state.pacman.pos
  const pcx = px * scale + scale / 2
  const pcy = (h - 1 - py) * scale + scale / 2
  const pr = Math.max(3, scale * 0.45)
  const dir = (state.pacman.dir || 'Stop')
  const dirMap = { North: -Math.PI/2, South: Math.PI/2, East: 0, West: Math.PI, Stop: 0 }
  drawPacman(ctx, pcx, pcy, pr, dirMap[dir] ?? 0)

  
  state.ghosts.forEach((g, idx) => {
    const [gx, gy] = g.pos
    const gcx = gx * scale + scale / 2
    const gcy = (h - 1 - gy) * scale + scale / 2
    const gr = Math.max(3, scale * 0.42)
    const color = GHOST_COLORS[idx % GHOST_COLORS.length]
    drawGhost(ctx, gcx, gcy, gr, color, g.scaredTimer > 0)
  })
}

const Game = ({ gameSettings, onBackToWelcome, modelInfo }) => {
  const [state, setState] = useState(null)
  const [auto, setAuto] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [speed, setSpeed] = useState(2) 
  const canvasRef = useRef(null)

  const reset = async () => {
    setIsLoading(true)
    try {
      const payload = { 
        layout: gameSettings.layoutName, 
        pacmanAgent: gameSettings.pacAgent, 
        ghostAgent: gameSettings.ghostAgent 
      }
      
      if (gameSettings.modelFile && modelInfo?.dir) {
        payload.modelPath = `${modelInfo.dir}/${gameSettings.modelFile}`
        payload.pacmanAgent = 'SaveLoadApproximateQAgent'
        payload.agentArgs = { extractor: 'SimpleExtractor', epsilon: 0.0, alpha: 0.0 }
      }
      
      const s = await apiReset(payload)
      setState(s)
    } catch (error) {
      console.error('Failed to reset game:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { reset() }, [gameSettings])

  const scale = useMemo(() => {
    if (!state) return 18
    const maxWidth = 900
    const target = Math.min(
      Math.floor(maxWidth / state.width),
      28
    )
    return Math.max(12, target)
  }, [state])

  useEffect(() => {
    if (!state) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    canvas.width = state.width * scale
    canvas.height = state.height * scale
    drawState(ctx, state, scale)
  }, [state, scale])

  useAnimationLoop(auto, async () => {
    try {
      const s = await apiStep(1)
      setState(s)
      if (s.isWin || s.isLose) setAuto(false)
    } catch (error) {
      console.error('Animation step failed:', error)
      setAuto(false)
    }
  }, speed)

  const handleStep = async () => {
    try {
      const s = await apiStep(1)
      setState(s)
    } catch (error) {
      console.error('Manual step failed:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <div className="loading-text">LOADING GAME...</div>
            <div className="loading-details">
              <div>Player: {gameSettings.username}</div>
              <div>Layout: {gameSettings.layoutName}</div>
              <div>Agent: {gameSettings.pacAgent}</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ textAlign: 'center', color: '#fff', background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)', minHeight: '100vh', fontFamily: '"Press Start 2P", monospace' }}>
      {}
      <div style={{
        background: '#000',
        padding: '20px',
        borderBottom: '3px solid #FFD700',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: '600px',
        margin: '0 auto'
      }}>
        <div style={{ fontSize: '14px' }}>
          <span style={{ color: '#FFD700' }}>PLAYER:</span> 
          <span style={{ color: '#00ffff', marginLeft: '10px' }}>{gameSettings.username}</span>
        </div>
        <div style={{ fontSize: '14px' }}>
          <span style={{ color: '#FFD700' }}>LAYOUT:</span> 
          <span style={{ color: '#00ffff', marginLeft: '10px' }}>
            {gameSettings.layoutName.replace(/([A-Z])/g, ' $1').toUpperCase()}
          </span>
        </div>
      </div>

      {}
      <div style={{
        background: '#111',
        padding: '15px',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        width: '600px',
        margin: '0 auto',
        borderLeft: '3px solid #FFD700',
        borderRight: '3px solid #FFD700'
      }}>
        <div>
          <div style={{ fontSize: '12px', color: '#FFD700', marginBottom: '5px' }}>SCORE</div>
          <div style={{ fontSize: '24px', color: '#fff' }}>{state?.score ?? 0}</div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: '#FFD700', marginBottom: '5px' }}>HIGH SCORE</div>
          <div style={{ fontSize: '24px', color: '#fff' }}>{Math.max(0, state?.score ?? 0)}</div>
        </div>
      </div>

      {}
      <div style={{ 
        position: 'relative',
        display: 'inline-block',
        background: '#000',
        border: '3px solid #FFD700',
        borderTop: 'none'
      }}>
        <canvas 
          ref={canvasRef} 
          width={600} 
          height={600}
          style={{ display: 'block' }}
        />
        
        {}
        {state && (state.isWin || state.isLose) && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
          }}>
            <h2 style={{ 
              fontSize: '36px', 
              color: state.isWin ? '#00ff00' : '#ff0000',
              marginBottom: '20px',
              textShadow: '2px 2px 4px #000'
            }}>
              {state.isWin ? 'YOU WIN!' : 'GAME OVER'}
            </h2>
            <div style={{ fontSize: '18px', color: '#FFD700', marginBottom: '30px' }}>
              FINAL SCORE: {state.score}
            </div>
          </div>
        )}

        {}
        {auto && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '36px',
            color: '#FFD700',
            textShadow: '2px 2px 4px #000',
            animation: 'blink 1s infinite'
          }}>
            AUTO MODE
          </div>
        )}
      </div>

      {}
      <div style={{
        background: '#111',
        padding: '20px',
        borderTop: '3px solid #FFD700',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: '600px',
        margin: '0 auto'
      }}>
        {}
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <button onClick={reset} style={buttonStyle}>RESET</button>
          <button onClick={handleStep} disabled={!state || auto} style={{...buttonStyle, opacity: (!state || auto) ? 0.5 : 1}}>STEP</button>
          <button onClick={() => setAuto(a => !a)} disabled={!state} style={{...buttonStyle, opacity: !state ? 0.5 : 1}}>
            {auto ? 'PAUSE' : 'AUTO'}
          </button>
          <button onClick={onBackToWelcome} style={buttonStyle}>MENU</button>
        </div>

        {}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '12px', color: '#FFD700', fontWeight: 'bold' }}>SPEED:</span>
          {[1, 2, 3, 4, 5].map(speedLevel => {
            const speedNames = { 1: 'SLOW', 2: 'NORM', 3: 'FAST', 4: 'V.FAST', 5: 'ULTRA' }
            return (
              <button
                key={speedLevel}
                onClick={() => setSpeed(speedLevel)}
                style={{
                  ...buttonStyle,
                  background: speed === speedLevel ? 'linear-gradient(145deg, #00ff00, #00aa00)' : 'linear-gradient(145deg, #666, #444)',
                  color: speed === speedLevel ? '#000' : '#fff',
                  padding: '6px 8px',
                  fontSize: '8px',
                  minWidth: '45px'
                }}
              >
                {speedNames[speedLevel]}
              </button>
            )
          })}
        </div>
      </div>

      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}

const buttonStyle = {
  background: 'linear-gradient(145deg, #FFD700, #FFA500)',
  border: 'none',
  color: '#000',
  padding: '10px 20px',
  fontSize: '12px',
  fontFamily: 'inherit',
  borderRadius: '5px',
  cursor: 'pointer',
  fontWeight: 'bold',
  transition: 'all 0.3s',
  letterSpacing: '1px'
}

export default Game
