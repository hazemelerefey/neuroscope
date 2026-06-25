import { useState } from 'react'
import UploadZone from './components/UploadZone'
import Canvas3D from './components/Canvas3D'
import AnalysisPanel from './components/AnalysisPanel'
import StatsPanel from './components/StatsPanel'
import ExportMenu from './components/ExportMenu'

function App() {
  const [graphData, setGraphData] = useState<any>(null)
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [selectedLayer, setSelectedLayer] = useState<any>(null)

  const handleUpload = (responseData: any) => {
    // Unwrap graph_json from the backend response into a flat structure
    setGraphData({
      ...responseData.graph_json,
      model_name: responseData.model_name,
      framework: responseData.framework,
      total_params: responseData.total_params,
      num_layers: responseData.num_layers,
    })
  }

  const handleReset = () => {
    setGraphData(null)
    setAnalysisData(null)
    setSelectedLayer(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🧠 NeuroScope</h1>
          <p>AI-Powered 3D Neural Network Architecture Visualizer & Analyzer</p>
        </div>
        {graphData && (
          <button className="reset-btn" onClick={handleReset}>
            📁 New Model
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
                onLayerClick={setSelectedLayer}
              />
            </div>
            <div className="panel-area">
              {selectedLayer && (
                <div className="layer-detail">
                  <h3>🔬 {selectedLayer.name}</h3>
                  <p><strong>Type:</strong> {selectedLayer.display_type}</p>
                  <p><strong>Category:</strong> {selectedLayer.category}</p>
                  <p><strong>Parameters:</strong> {selectedLayer.formatted_params}</p>
                  {selectedLayer.description && <p>{selectedLayer.description}</p>}
                  <button onClick={() => setSelectedLayer(null)}>✕ Close</button>
                </div>
              )}
              <StatsPanel graphData={graphData} analysisData={analysisData} />
              <AnalysisPanel
                graphData={graphData}
                onAnalysisComplete={setAnalysisData}
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
