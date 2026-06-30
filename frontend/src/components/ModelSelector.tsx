import { useState } from 'react'
import { ChevronRight, ChevronDown, Check } from 'lucide-react'
import { useStore } from '../store'
import type { ModelFamily, ModelVersion, ModelSize, SelectedModel } from '../types'

export default function ModelSelector() {
  const catalog = useStore((s) => s.modelCatalog)
  const selectModel = useStore((s) => s.selectModel)
  const selectedModel = useStore((s) => s.selectedModel)

  const [expandedFamily, setExpandedFamily] = useState<string | null>(null)
  const [expandedVersion, setExpandedVersion] = useState<string | null>(null)

  const handleSizeClick = (family: ModelFamily, version: ModelVersion, size: ModelSize) => {
    const selection: SelectedModel = { family, version, size }
    selectModel(selection)
  }

  return (
    <div className="model-selector">
      <h3 className="panel-title">🏗️ Model Selector</h3>
      <p className="panel-subtitle">Choose a model family, version, and size</p>

      <div className="model-tree">
        {catalog.map((family) => (
          <div key={family.id} className="tree-family">
            <button
              className={`tree-toggle ${expandedFamily === family.id ? 'expanded' : ''}`}
              onClick={() => setExpandedFamily(expandedFamily === family.id ? null : family.id)}
            >
              {expandedFamily === family.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              <span className="tree-icon">{family.icon}</span>
              <span className="tree-label">{family.name}</span>
            </button>

            {expandedFamily === family.id && (
              <div className="tree-children">
                <p className="family-desc">{family.description}</p>
                {family.versions.map((version) => (
                  <div key={version.id} className="tree-version">
                    <button
                      className={`tree-toggle sub ${expandedVersion === version.id ? 'expanded' : ''}`}
                      onClick={() => setExpandedVersion(expandedVersion === version.id ? null : version.id)}
                    >
                      {expandedVersion === version.id ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                      <span className="tree-label">{version.name}</span>
                    </button>

                    {expandedVersion === version.id && (
                      <div className="tree-sizes">
                        {version.sizes.map((size) => {
                          const isSelected =
                            selectedModel?.family.id === family.id &&
                            selectedModel?.version.id === version.id &&
                            selectedModel?.size.id === size.id

                          return (
                            <button
                              key={size.id}
                              className={`size-option ${isSelected ? 'selected' : ''}`}
                              onClick={() => handleSizeClick(family, version, size)}
                            >
                              <div className="size-header">
                                <span className="size-name">{size.name}</span>
                                <span className="size-params">{size.params}</span>
                                {isSelected && <Check size={14} className="check-icon" />}
                              </div>
                              <div className="size-desc">{size.description}</div>
                              <div className="size-complexity">
                                {Array.from({ length: 5 }, (_, i) => (
                                  <span
                                    key={i}
                                    className={`complexity-dot ${i < size.complexity ? 'filled' : ''}`}
                                  />
                                ))}
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
