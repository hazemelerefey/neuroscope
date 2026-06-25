import { useState } from 'react'
import axios from 'axios'
import { Search, AlertTriangle, AlertCircle, Info, Filter } from 'lucide-react'
import type { GraphData, AnalysisReport, Finding } from '../types'

interface AnalysisPanelProps {
  graphData: GraphData
  onAnalysisComplete: (data: AnalysisReport) => void
}

type SeverityFilter = 'all' | 'CRITICAL' | 'WARNING' | 'INFO'

export default function AnalysisPanel({ graphData, onAnalysisComplete }: AnalysisPanelProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<AnalysisReport | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all')

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const response = await axios.post<AnalysisReport>('/api/analyze', {
        model_id: graphData.model_name,
      })
      setResults(response.data)
      onAnalysisComplete(response.data)
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
      } else {
        setError('Analysis failed. Please try again.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertCircle size={14} style={{ color: 'var(--accent-red)' }} />
      case 'WARNING': return <AlertTriangle size={14} style={{ color: 'var(--accent-yellow)' }} />
      default: return <Info size={14} style={{ color: 'var(--accent-green)' }} />
    }
  }

  const filteredFindings = results?.findings.filter(
    (f) => severityFilter === 'all' || f.severity === severityFilter
  ) || []

  const handleFindingClick = (finding: Finding) => {
    if (finding.layer_ids.length > 0) {
      // Could highlight layers in the 3D view — for now just log
      console.log('Finding layers:', finding.layer_ids)
    }
  }

  return (
    <div className="analysis-panel">
      <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Search size={16} />
        Architecture Analysis
      </h3>

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

          {/* Severity filter */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 12, alignItems: 'center' }}>
            <Filter size={13} style={{ color: 'var(--text-secondary)', marginRight: 4 }} />
            {(['all', 'CRITICAL', 'WARNING', 'INFO'] as SeverityFilter[]).map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                style={{
                  padding: '3px 8px',
                  fontSize: 11,
                  borderRadius: 4,
                  border: '1px solid',
                  borderColor: severityFilter === sev ? 'var(--accent-blue)' : 'var(--border)',
                  background: severityFilter === sev ? 'rgba(59,130,246,0.15)' : 'transparent',
                  color: severityFilter === sev ? 'var(--accent-blue)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                }}
              >
                {sev === 'all' ? 'All' : sev}
              </button>
            ))}
          </div>

          <div className="findings-list">
            {filteredFindings.map((finding, i) => (
              <div
                key={i}
                className={`finding finding-${finding.severity.toLowerCase()}`}
                onClick={() => handleFindingClick(finding)}
                style={{ cursor: finding.layer_ids.length > 0 ? 'pointer' : 'default' }}
              >
                <div className="finding-header">
                  {getSeverityIcon(finding.severity)}
                  <span className="title">{finding.title}</span>
                  <span className="rule-id">{finding.rule_id}</span>
                </div>
                <p className="message">{finding.message}</p>
                <p className="fix">💡 {finding.fix}</p>
              </div>
            ))}
            {filteredFindings.length === 0 && (
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, textAlign: 'center', padding: 12 }}>
                No findings matching this filter.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
