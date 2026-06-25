import { useStore } from './store'
import { Brain, RotateCcw } from 'lucide-react'
import UploadZone from './components/UploadZone'
import Canvas3D from './components/Canvas3D'
import AnalysisPanel from './components/AnalysisPanel'
import StatsPanel from './components/StatsPanel'
import ExportMenu from './components/ExportMenu'
import LayerDetail from './components/LayerDetail'
import type { UploadResponse } from './types'

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
              <Canvas3D
                graphData={graphData}
                onLayerClick={selectLayer}
              />
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
              <ExportMenu modelId={graphData.model_name} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
