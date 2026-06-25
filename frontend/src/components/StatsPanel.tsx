import { Layers, Hash, Cpu, Zap, HardDrive, LayoutGrid } from 'lucide-react'
import type { GraphData, AnalysisReport } from '../types'

interface StatsPanelProps {
  graphData: GraphData
  analysisData: AnalysisReport | null
}

export default function StatsPanel({ graphData, analysisData }: StatsPanelProps) {
  const formatNumber = (n: number) => {
    if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`
    if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`
    if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`
    return n.toString()
  }

  return (
    <div className="stats-panel">
      <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <LayoutGrid size={16} />
        Model Statistics
      </h3>

      <div className="stats-grid">
        <div className="stat">
          <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Layers size={12} /> Layers
          </span>
          <span className="stat-value">{graphData?.nodes?.length || 0}</span>
        </div>

        <div className="stat">
          <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Hash size={12} /> Parameters
          </span>
          <span className="stat-value">{formatNumber(graphData?.total_params || 0)}</span>
        </div>

        <div className="stat">
          <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Cpu size={12} /> Framework
          </span>
          <span className="stat-value">{graphData?.framework || 'Unknown'}</span>
        </div>

        {analysisData && (
          <>
            <div className="stat">
              <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Zap size={12} /> FLOPs
              </span>
              <span className="stat-value">{formatNumber(analysisData.total_flops)}</span>
            </div>

            <div className="stat">
              <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <HardDrive size={12} /> Memory
              </span>
              <span className="stat-value">{analysisData.total_memory_mb?.toFixed(1)} MB</span>
            </div>

            <div className="stat">
              <span className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Cpu size={12} /> Architecture
              </span>
              <span className="stat-value">{analysisData.architecture_type}</span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
