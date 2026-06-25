import { useState } from 'react'
import axios from 'axios'

interface ExportMenuProps {
  modelId: string
}

export default function ExportMenu({ modelId }: ExportMenuProps) {
  const [error, setError] = useState<string | null>(null)

  const handleExport = async (format: string) => {
    setError(null)
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
    } catch (err: any) {
      setError(err.response?.data?.detail || `Export to ${format} failed.`)
      console.error('Export failed:', err)
    }
  }

  return (
    <div className="export-menu">
      <h3>📤 Export</h3>
      <div className="export-buttons">
        <button onClick={() => handleExport('markdown')}>📄 Report (MD)</button>
        <button onClick={() => handleExport('html')}>🌐 3D Viewer (HTML)</button>
        <button onClick={() => handleExport('svg')} disabled>📐 Diagram (SVG)</button>
        <button onClick={() => handleExport('glb')} disabled>🎮 3D Model (GLB)</button>
        <button onClick={() => handleExport('pdf')} disabled>📑 Report (PDF)</button>
      </div>
      {error && <p className="error" style={{ marginTop: 8 }}>{error}</p>}
    </div>
  )
}
