import axios from 'axios'

interface ExportMenuProps {
  modelId: string
}

export default function ExportMenu({ modelId }: ExportMenuProps) {
  const handleExport = async (format: string) => {
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
    } catch (err) {
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
    </div>
  )
}
