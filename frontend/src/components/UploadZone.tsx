import { useState, useCallback } from 'react'
import axios from 'axios'

interface UploadZoneProps {
  onUpload: (data: any) => void
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(async (file: File) => {
    setIsUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onUpload(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }, [onUpload])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleClick = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.onnx,.pt,.pth,.h5,.keras,.tflite'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) handleFile(file)
    }
    input.click()
  }, [handleFile])

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleClick}
    >
      {isUploading ? (
        <div className="upload-spinner">
          <div className="spinner" />
          <p>Parsing model...</p>
        </div>
      ) : (
        <>
          <div className="upload-icon">📁</div>
          <h2>Upload Your Model</h2>
          <p>Drag & drop a model file here, or click to browse</p>
          <p className="formats">Supported: .onnx, .pt, .pth, .h5, .keras, .tflite</p>
          {error && <p className="error">{error}</p>}
        </>
      )}
    </div>
  )
}
