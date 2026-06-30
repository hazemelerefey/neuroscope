import { useState, useEffect } from 'react'
import { Code, X, Copy, Check, Download } from 'lucide-react'
import { useStore } from '../store'
import type { ExportFormat } from '../types'

export default function NotebookWindow() {
  const notebookOpen = useStore((s) => s.notebookOpen)
  const toggleNotebook = useStore((s) => s.toggleNotebook)
  const exportNotebook = useStore((s) => s.exportNotebook)
  const selectedModel = useStore((s) => s.selectedModel)
  const extensions = useStore((s) => s.extensions)

  const [activeFormat, setActiveFormat] = useState<ExportFormat>('ipynb')
  const [copied, setCopied] = useState(false)
  const [content, setContent] = useState('')

  useEffect(() => {
    if (notebookOpen && selectedModel) {
      const result = exportNotebook(activeFormat)
      setContent(result)
    }
  }, [notebookOpen, selectedModel, extensions, activeFormat, exportNotebook])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const ext = activeFormat === 'ipynb' ? 'ipynb' : 'yaml'
    const mime = activeFormat === 'ipynb' ? 'application/json' : 'text/yaml'
    const blob = new Blob([content], { type: mime })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `neuroscope_model.${ext}`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!notebookOpen || !selectedModel) return null

  return (
    <div className="notebook-window">
      <div className="notebook-header">
        <div className="notebook-title">
          <Code size={14} />
          <span>Notebook</span>
        </div>
        <div className="notebook-tabs">
          <button
            className={`tab ${activeFormat === 'ipynb' ? 'active' : ''}`}
            onClick={() => setActiveFormat('ipynb')}
          >
            .ipynb
          </button>
          <button
            className={`tab ${activeFormat === 'yaml' ? 'active' : ''}`}
            onClick={() => setActiveFormat('yaml')}
          >
            .yaml
          </button>
        </div>
        <div className="notebook-actions">
          <button onClick={handleCopy} className="action-btn" title="Copy">
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </button>
          <button onClick={handleDownload} className="action-btn" title="Download">
            <Download size={14} />
          </button>
          <button onClick={toggleNotebook} className="action-btn" title="Close">
            <X size={14} />
          </button>
        </div>
      </div>

      <div className="notebook-body">
        <pre className="notebook-code">
          <code>{content}</code>
        </pre>
      </div>
    </div>
  )
}
