import { X, Cpu, Tag, Hash, FileText } from 'lucide-react'
import type { LayerNode } from '../types'

interface LayerDetailProps {
  layer: LayerNode
  onClose: () => void
}

export default function LayerDetail({ layer, onClose }: LayerDetailProps) {
  return (
    <div className="layer-detail">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Cpu size={16} />
          {layer.name}
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: 4,
          }}
          aria-label="Close layer detail"
        >
          <X size={16} />
        </button>
      </div>

      <p style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Tag size={13} />
        <strong>Type:</strong> {layer.display_type}
      </p>
      <p style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Hash size={13} />
        <strong>Category:</strong> {layer.category}
      </p>
      <p style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Cpu size={13} />
        <strong>Parameters:</strong> {layer.formatted_params}
      </p>
      {layer.description && (
        <p style={{ display: 'flex', alignItems: 'flex-start', gap: 6, marginTop: 4 }}>
          <FileText size={13} style={{ flexShrink: 0, marginTop: 2 }} />
          {layer.description}
        </p>
      )}

      {layer.input_shapes.length > 0 && (
        <p>
          <strong>Input:</strong>{' '}
          {layer.input_shapes.map((s, i) => (
            <span key={i} style={{ fontFamily: 'monospace', fontSize: 12 }}>
              [{s.join(', ')}]{i < layer.input_shapes.length - 1 ? ', ' : ''}
            </span>
          ))}
        </p>
      )}
      {layer.output_shapes.length > 0 && (
        <p>
          <strong>Output:</strong>{' '}
          {layer.output_shapes.map((s, i) => (
            <span key={i} style={{ fontFamily: 'monospace', fontSize: 12 }}>
              [{s.join(', ')}]{i < layer.output_shapes.length - 1 ? ', ' : ''}
            </span>
          ))}
        </p>
      )}
    </div>
  )
}
