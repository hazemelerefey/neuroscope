import { useStore } from './store'
import { Brain, RotateCcw, Code, Layers } from 'lucide-react'
import Canvas3D from './components/Canvas3D'
import ModelSelector from './components/ModelSelector'
import ExtensionConfig from './components/ExtensionConfig'
import InfoPanel from './components/InfoPanel'
import NotebookWindow from './components/NotebookWindow'
import DevelopMode from './components/DevelopMode'
import { Component, type ReactNode } from 'react'

// Error Boundary for 3D Canvas
class CanvasErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error: string }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false, error: '' }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          padding: '2rem',
          textAlign: 'center',
          color: '#64748b',
        }}>
          <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
            3D visualization failed to render
          </p>
          <p style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
            {this.state.error}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: '' })}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
            }}
          >
            Try Again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const selectedModel = useStore((s) => s.selectedModel)
  const selectedExtensionKind = useStore((s) => s.selectedExtensionKind)
  const rightPanelTab = useStore((s) => s.rightPanelTab)
  const developMode = useStore((s) => s.developMode)
  const notebookOpen = useStore((s) => s.notebookOpen)
  const clearModel = useStore((s) => s.clearModel)
  const toggleDevelopMode = useStore((s) => s.toggleDevelopMode)
  const toggleNotebook = useStore((s) => s.toggleNotebook)
  const selectExtension = useStore((s) => s.selectExtension)

  const handleExtensionClose = () => {
    selectExtension(null as never)
    useStore.getState().setRightPanelTab('model')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <Brain size={24} />
            NeuroScope
          </h1>
          <p>Visual Deep Learning Builder</p>
        </div>

        <div className="header-actions">
          {selectedModel && (
            <>
              <button
                className={`toolbar-btn ${developMode ? 'active' : ''}`}
                onClick={toggleDevelopMode}
                title="Develop Mode — inspect and modify layers"
              >
                <Layers size={14} />
                <span>Develop</span>
              </button>
              <button
                className={`toolbar-btn ${notebookOpen ? 'active' : ''}`}
                onClick={toggleNotebook}
                title="Toggle Notebook"
              >
                <Code size={14} />
                <span>Notebook</span>
              </button>
              <button className="toolbar-btn" onClick={clearModel} title="Start over">
                <RotateCcw size={14} />
                <span>Reset</span>
              </button>
            </>
          )}
        </div>
      </header>

      <main className="app-main">
        <div className="workspace">
          {/* Left: 3D Canvas */}
          <div className="canvas-area">
            <CanvasErrorBoundary>
              <Canvas3D />
            </CanvasErrorBoundary>
          </div>

          {/* Right: Panel area */}
          <div className="panel-area">
            {rightPanelTab === 'model' ? (
              <ModelSelector />
            ) : selectedExtensionKind ? (
              <ExtensionConfig
                kind={selectedExtensionKind}
                onClose={handleExtensionClose}
              />
            ) : (
              <ModelSelector />
            )}
          </div>

          {/* Develop mode overlay (below canvas, above info) */}
          {developMode && selectedModel && (
            <div className="develop-panel">
              <DevelopMode />
            </div>
          )}

          {/* Notebook window (top-right overlay) */}
          {notebookOpen && (
            <NotebookWindow />
          )}

          {/* Info panel (bottom) */}
          {selectedModel && (
            <InfoPanel />
          )}
        </div>
      </main>
    </div>
  )
}

export default App
