import { useState } from 'react'
import axios from 'axios'

interface AnalysisPanelProps {
  graphData: any
  onAnalysisComplete: (data: any) => void
}

export default function AnalysisPanel({ graphData, onAnalysisComplete }: AnalysisPanelProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const response = await axios.post('/api/analyze', {
        model_id: graphData.model_name,
      })
      setResults(response.data)
      onAnalysisComplete(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
      console.error('Analysis failed:', err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="analysis-panel">
      <h3>🔍 Architecture Analysis</h3>

      {!results ? (
        <>
          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
          </button>
          {error && <p className="error" style={{ marginTop: 8 }}>{error}</p>}
        </>
      ) : (
        <div className="analysis-results">
          <div className="health-score">
            <div className={`grade grade-${results.health_grade.toLowerCase()}`}>
              {results.health_grade}
            </div>
            <div className="score-details">
              <span className="score">{results.health_score}/100</span>
              <span className="counts">
                🔴 {results.critical_count} &nbsp;
                🟡 {results.warning_count} &nbsp;
                🟢 {results.info_count}
              </span>
            </div>
          </div>

          <div className="findings-list">
            {results.findings.map((finding: any, i: number) => (
              <div key={i} className={`finding finding-${finding.severity.toLowerCase()}`}>
                <div className="finding-header">
                  <span className="icon">{finding.icon}</span>
                  <span className="title">{finding.title}</span>
                  <span className="rule-id">{finding.rule_id}</span>
                </div>
                <p className="message">{finding.message}</p>
                <p className="fix">💡 {finding.fix}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
