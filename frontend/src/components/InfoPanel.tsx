import { Info, ChevronDown, ChevronUp, Layers, Cpu, Zap, HardDrive } from 'lucide-react'
import { useStore } from '../store'

export default function InfoPanel() {
  const selectedModel = useStore((s) => s.selectedModel)
  const extensions = useStore((s) => s.extensions)
  const collapsed = useStore((s) => s.infoPanelCollapsed)
  const toggleInfoPanel = useStore((s) => s.toggleInfoPanel)

  const configuredCount = extensions.filter((e) => e.selectedOptionId).length

  if (!selectedModel) return null

  const formatParams = (p: string) => p

  return (
    <div className={`info-panel ${collapsed ? 'collapsed' : ''}`}>
      <button className="info-toggle" onClick={toggleInfoPanel}>
        <Info size={14} />
        <span>Model Info</span>
        {collapsed ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {!collapsed && (
        <div className="info-content">
          <div className="info-model">
            <h4>
              {selectedModel.family.icon} {selectedModel.version.name} {selectedModel.size.name}
            </h4>
            <p className="info-description">{selectedModel.size.description}</p>
          </div>

          <div className="info-stats">
            <div className="info-stat">
              <Layers size={13} />
              <span className="stat-label">Family</span>
              <span className="stat-value">{selectedModel.family.name}</span>
            </div>
            <div className="info-stat">
              <Cpu size={13} />
              <span className="stat-label">Parameters</span>
              <span className="stat-value">{formatParams(selectedModel.size.params)}</span>
            </div>
            <div className="info-stat">
              <Zap size={13} />
              <span className="stat-label">Complexity</span>
              <span className="stat-value">
                {Array.from({ length: 5 }, (_, i) => (
                  <span
                    key={i}
                    className={`dot ${i < selectedModel.size.complexity ? 'filled' : ''}`}
                  />
                ))}
              </span>
            </div>
            <div className="info-stat">
              <HardDrive size={13} />
              <span className="stat-label">Extensions</span>
              <span className="stat-value">{configuredCount} / {extensions.length}</span>
            </div>
          </div>

          {configuredCount > 0 && (
            <div className="info-extensions">
              <h4>Configured Extensions</h4>
              <div className="info-ext-list">
                {extensions
                  .filter((e) => e.selectedOptionId)
                  .map((ext) => {
                    const opt = ext.options.find((o) => o.id === ext.selectedOptionId)
                    return (
                      <div key={ext.kind} className="info-ext-item">
                        <span className="ext-icon">{ext.icon}</span>
                        <span className="ext-label">{ext.label}</span>
                        <span className="ext-value">{opt?.name}</span>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
