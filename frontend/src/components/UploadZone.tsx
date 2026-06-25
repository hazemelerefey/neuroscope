import { useState, useCallback, useRef } from 'react'
import axios from 'axios'
import { Upload, AlertCircle } from 'lucide-react'
import type { UploadResponse } from '../types'

interface UploadZoneProps {
  onUpload: (data: UploadResponse) => void
}

const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB
const SUPPORTED_EXTENSIONS = ['.onnx', '.pt', '.pth', '.h5', '.keras', '.tflite']

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(async (file: File) => {
    // Validate extension
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!SUPPORTED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported format: ${ext}. Supported: ${SUPPORTED_EXTENSIONS.join(', ')}`)
      return
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setError(`File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max: 500MB`)
      return
    }

    setIsUploading(true)
    setProgress(0)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post<UploadResponse>('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 100))
        },
      })
      onUpload(response.data)
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Upload failed')
      } else {
        setError('Upload failed')
      }
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
    inputRef.current?.click()
  }, [])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    // Reset input so same file can be re-selected
    e.target.value = ''
  }, [handleFile])

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept={SUPPORTED_EXTENSIONS.join(',')}
        onChange={handleInputChange}
        style={{ display: 'none' }}
      />

      {isUploading ? (
        <div className="upload-spinner">
          <div className="spinner" />
          <p>Parsing model...</p>
          {progress > 0 && (
            <div style={{ width: '60%', marginTop: 8 }}>
              <div style={{
                height: 4,
                background: 'var(--border)',
                borderRadius: 2,
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${progress}%`,
                  background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-purple))',
                  transition: 'width 0.2s',
                }} />
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                {progress}%
              </p>
            </div>
          )}
        </div>
      ) : (
        <>
          <Upload size={48} style={{ color: 'var(--text-secondary)', marginBottom: 16 }} />
          <h2>Upload Your Model</h2>
          <p>Drag & drop a model file here, or click to browse</p>
          <p className="formats">Supported: {SUPPORTED_EXTENSIONS.join(', ')} · Max 500MB</p>
          {error && (
            <p className="error" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <AlertCircle size={14} />
              {error}
            </p>
          )}
        </>
      )}
    </div>
  )
}
