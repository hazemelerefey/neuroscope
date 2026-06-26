import { useState } from 'react'
import axios from 'axios'
import { Download, FileText, Globe, Loader2 } from 'lucide-react'

interface ExportMenuProps {
  modelId: string
}

interface ExportOption {
  format: string
  label: string
  icon: React.ReactNode
  enabled: boolean
}

const EXPORT_OPTIONS: ExportOption[] = [
  { format: 'json', label: 'Full Data (JSON)', icon: <FileText size={14} />, enabled: true },
  { format: 'summary', label: 'Report (TXT)', icon: <FileText size={14} />, enabled: true },
  { format: 'png', label: 'Diagram (PNG)', icon: <FileText size={14} />, enabled: true },
]

export default function ExportMenu({ modelId }: ExportMenuProps) {
  const [error, setError] = useState<string | null>(null)
  const [loadingFormat, setLoadingFormat] = useState<string | null>(null)

  const handleExport = async (format: string) => {
    setError(null)
    setLoadingFormat(format)
    try {
      const response = await axios.post(
        '/api/export',
        { model_id: modelId, format },
        { responseType: 'blob' }
      )

      // Download the file
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `neuroscope_${modelId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        // Blob errors need special handling — try to read as text
        const data = err.response?.data
        if (data instanceof Blob) {
          try {
            const text = await data.text()
            const parsed = JSON.parse(text)
            setError(parsed.detail || `Export to ${format} failed.`)
          } catch {
            setError(`Export to ${format} failed.`)
          }
        } else {
          setError(data?.detail || `Export to ${format} failed.`)
        }
      } else {
        setError(`Export to ${format} failed.`)
      }
    } finally {
      setLoadingFormat(null)
    }
  }

  return (
    <div className="export-menu">
      <h3 style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <Download size={16} />
        Export
      </h3>
      <div className="export-buttons">
        {EXPORT_OPTIONS.map((opt) => (
          <button
            key={opt.format}
            onClick={() => handleExport(opt.format)}
            disabled={!opt.enabled || loadingFormat !== null}
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}
          >
            {loadingFormat === opt.format ? (
              <Loader2 size={14} className="spinner" style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : (
              opt.icon
            )}
            {opt.label}
          </button>
        ))}
      </div>
      {error && <p className="error" style={{ marginTop: 8 }}>{error}</p>}
    </div>
  )
}
