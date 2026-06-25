import { useState } from 'react'
import UploadZone from './components/UploadZone'
import Canvas3D from './components/Canvas3D'
import AnalysisPanel from './components/AnalysisPanel'
import StatsPanel from './components/StatsPanel'
import ExportMenu from './components/ExportMenu'

function App() {
  const [graphData, setGraphData] = useState(null)
  const [analysisData, setAnalysisData] = useState(null)
  const [selectedLayer, setSelectedLayer] = useState(null)

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 NeuroScope</h1>
        <p>AI-Powered 3D Neural Network Architecture Visualizer & Analyzer</p>
      </header>

      <main className="app-main">
        {!graphData ? (
          <UploadZone onUpload={setGraphData} />
        ) : (
          <div className="workspace">
            <div className="canvas-area">
              <Canvas3D
                graphData={graphData}
                onLayerClick={setSelectedLayer}
              />
            </div>
            <div className="panel-area">
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
