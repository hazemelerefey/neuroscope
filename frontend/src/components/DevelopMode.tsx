import { useState } from 'react'
import { Snowflake, Trash2, Plus, ChevronDown, ChevronRight } from 'lucide-react'
import { useStore } from '../store'

const ADDABLE_LAYER_TYPES = ['Conv2d', 'Linear', 'BatchNorm2d', 'ReLU', 'GELU', 'Dropout', 'MaxPool2d']

export default function DevelopMode() {
  const layers = useStore((s) => s.layers)
  const toggleFrozen = useStore((s) => s.toggleLayerFrozen)
  const removeLayer = useStore((s) => s.removeLayer)
  const addLayer = useStore((s) => s.addLayer)
  const [expandedLayer, setExpandedLayer] = useState<string | null>(null)
  const [addAfterId, setAddAfterId] = useState<string | null>(null)

  if (layers.length === 0) return null

  return (
    <div className="develop-mode">
      <h4 className="develop-title">🔬 Layer Inspector</h4>

      <div className="layer-list">
        {layers.map((layer, idx) => (
          <div key={layer.id} className={`layer-item ${layer.frozen ? 'frozen' : ''}`}>
            <div className="layer-row">
              <button
                className="layer-expand"
                onClick={() => setExpandedLayer(expandedLayer === layer.id ? null : layer.id)}
              >
                {expandedLayer === layer.id ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
              </button>

              <div className="layer-info">
                <span className="layer-type-badge" data-type={layer.type.toLowerCase()}>
                  {layer.type}
                </span>
                <span className="layer-name">{layer.name}</span>
                {layer.params > 0 && (
                  <span className="layer-params">{formatParamCount(layer.params)}</span>
                )}
              </div>

              <div className="layer-actions">
                <button
                  className={`action-btn freeze ${layer.frozen ? 'active' : ''}`}
                  onClick={() => toggleFrozen(layer.id)}
                  title={layer.frozen ? 'Unfreeze' : 'Freeze'}
                >
                  <Snowflake size={12} />
                </button>
                <button
                  className="action-btn add"
                  onClick={() => setAddAfterId(addAfterId === layer.id ? null : layer.id)}
                  title="Add layer after"
                >
                  <Plus size={12} />
                </button>
                {layer.removable && (
                  <button
                    className="action-btn remove"
                    onClick={() => removeLayer(layer.id)}
                    title="Remove layer"
                  >
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
            </div>

            {expandedLayer === layer.id && (
              <div className="layer-details">
                <div className="detail-row">
                  <span className="detail-label">Input</span>
                  <code className="detail-value">{layer.inputShape}</code>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Output</span>
                  <code className="detail-value">{layer.outputShape}</code>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Parameters</span>
                  <code className="detail-value">{layer.params.toLocaleString()}</code>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Status</span>
                  <span className={`status-badge ${layer.frozen ? 'frozen' : 'trainable'}`}>
                    {layer.frozen ? '❄️ Frozen' : '🔥 Trainable'}
                  </span>
                </div>
              </div>
            )}

            {addAfterId === layer.id && (
              <div className="add-layer-menu">
                <span className="menu-label">Insert after {layer.name}:</span>
                <div className="layer-type-options">
                  {ADDABLE_LAYER_TYPES.map((type) => (
                    <button
                      key={type}
                      className="type-option"
                      onClick={() => {
                        addLayer(layer.id, type)
                        setAddAfterId(null)
                      }}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {idx < layers.length - 1 && (
              <div className="layer-connector">
                <div className="connector-line" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function formatParamCount(n: number): string {
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n.toString()
}
