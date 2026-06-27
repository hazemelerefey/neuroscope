import { useStore } from './store'
import { Brain, RotateCcw } from 'lucide-react'
import UploadZone from './components/UploadZone'
import Canvas3D from './components/Canvas3D'
import AnalysisPanel from './components/AnalysisPanel'
import StatsPanel from './components/StatsPanel'
import ExportMenu from './components/ExportMenu'
import LayerDetail from './components/LayerDetail'
import type { UploadResponse } from './types'
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
  const graphData = useStore((s) => s.graphData)
  const analysisData = useStore((s) => s.analysisData)
  const selectedLayer = useStore((s) => s.selectedLayer)
  const setGraphData = useStore((s) => s.setGraphData)
  const selectLayer = useStore((s) => s.selectLayer)
  const reset = useStore((s) => s.reset)

  const handleUpload = (responseData: UploadResponse) => {
    const gj = responseData.graph_json
    setGraphData({
      model_id: responseData.model_id,
      nodes: gj.nodes,
      edges: gj.edges,
      model_name: responseData.model_name,
      framework: responseData.framework,
      input_shapes: gj.input_shapes,
      output_shapes: gj.output_shapes,
      total_params: responseData.total_params,
      total_flops: gj.total_flops,
      total_memory_bytes: gj.total_memory_bytes,
      architecture_type: gj.architecture_type,
    })
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <Brain size={24} />
            NeuroScope
          </h1>
          <p>AI-Powered 3D Neural Network Architecture Visualizer & Analyzer</p>
        </div>
        {graphData && (
          <button className="reset-btn" onClick={reset}>
            <RotateCcw size={14} style={{ marginRight: 6 }} />
            New Model
          </button>
        )}
      </header>

      <main className="app-main">
        {!graphData ? (
          <UploadZone onUpload={handleUpload} />
        ) : (
          <div className="workspace">
            <div className="canvas-area">
              <CanvasErrorBoundary>
                <Canvas3D
                  graphData={graphData}
                  onLayerClick={selectLayer}
                />
              </CanvasErrorBoundary>
            </div>
            <div className="panel-area">
              {selectedLayer && (
                <LayerDetail
                  layer={selectedLayer}
                  onClose={() => selectLayer(null)}
                />
              )}
              <StatsPanel graphData={graphData} analysisData={analysisData} />
              <AnalysisPanel
                graphData={graphData}
                onAnalysisComplete={useStore.getState().setAnalysisData}
              />
              <ExportMenu modelId={graphData.model_id} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
