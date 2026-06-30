import { X, Check } from 'lucide-react'
import { useStore } from '../store'
import type { ExtensionKind } from '../types'

interface ExtensionConfigProps {
  kind: ExtensionKind
  onClose: () => void
}

export default function ExtensionConfig({ kind, onClose }: ExtensionConfigProps) {
  const extension = useStore((s) => s.extensions.find((e) => e.kind === kind))
  const updateOption = useStore((s) => s.updateExtensionOption)

  if (!extension) return null


  return (
    <div className="extension-config">
      <div className="config-header">
        <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span>{extension.icon}</span>
          {extension.label}
        </h3>
        <button onClick={onClose} className="close-btn" aria-label="Close">
          <X size={16} />
        </button>
      </div>

      <div className="config-options">
        {extension.options.map((opt) => {
          const isSelected = extension.selectedOptionId === opt.id
          return (
            <div key={opt.id} className="config-option-wrapper">
              <button
                className={`config-option ${isSelected ? 'selected' : ''}`}
                onClick={() => updateOption(kind, opt.id)}
              >
                <div className="option-header">
                  <span className="option-name">{opt.name}</span>
                  {isSelected && <Check size={14} className="check-icon" />}
                </div>
                <p className="option-desc">{opt.description}</p>
              </button>

              {isSelected && (
                <div className="option-details">
                  <div className="detail-section">
                    <span className="detail-label">💡 When to use</span>
                    <p>{opt.whenToUse}</p>
                  </div>
                  <div className="detail-section">
                    <span className="detail-label">⚡ Consequences</span>
                    <p>{opt.consequences}</p>
                  </div>
                  <div className="detail-section code">
                    <span className="detail-label">📝 Code</span>
                    <pre><code>{opt.code}</code></pre>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
