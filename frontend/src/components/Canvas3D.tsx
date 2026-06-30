import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Html, Line } from '@react-three/drei'
import { Color, type Group } from 'three'
import { useStore } from '../store'
import type { Extension, SelectedModel } from '../types'

// ─── Empty state: + button ────────────────────────────────────────

function EmptyState() {
  return (
    <Html center>
      <div
        className="empty-canvas"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 12,
          userSelect: 'none',
        }}
      >
        <div
          className="plus-button"
          onClick={() => {
            // Trigger right panel to show model selector
            useStore.getState().setRightPanelTab('model')
          }}
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            border: '2px dashed rgba(99,102,241,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            fontSize: 36,
            color: 'rgba(99,102,241,0.7)',
            transition: 'all 0.2s',
            background: 'rgba(99,102,241,0.05)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.border = '2px solid rgba(99,102,241,0.8)'
            e.currentTarget.style.background = 'rgba(99,102,241,0.1)'
            e.currentTarget.style.transform = 'scale(1.05)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.border = '2px dashed rgba(99,102,241,0.5)'
            e.currentTarget.style.background = 'rgba(99,102,241,0.05)'
            e.currentTarget.style.transform = 'scale(1)'
          }}
        >
          +
        </div>
        <p style={{ color: '#64748b', fontSize: 14, fontFamily: 'Inter, sans-serif' }}>
          Select a model to begin
        </p>
      </div>
    </Html>
  )
}

// ─── Core engine block ────────────────────────────────────────────

function CoreEngine({ model }: { model: SelectedModel }) {
  const ref = useRef<Group>(null!)
  const complexity = model.size.complexity
  const baseScale = 0.5 + complexity * 0.15

  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta * 0.2
    }
  })

  const color = new Color(
    model.family.id === 'cnn' ? '#6366f1' :
    model.family.id === 'yolo' ? '#f59e0b' :
    model.family.id === 'resnet' ? '#10b981' :
    model.family.id === 'transformer' ? '#8b5cf6' :
    model.family.id === 'gan' ? '#ec4899' : '#06b6d4'
  )

  return (
    <group ref={ref}>
      {/* Main block */}
      <mesh>
        <boxGeometry args={[baseScale, baseScale, baseScale]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.85}
          roughness={0.3}
          metalness={0.6}
        />
      </mesh>

      {/* Wireframe overlay */}
      <mesh>
        <boxGeometry args={[baseScale + 0.02, baseScale + 0.02, baseScale + 0.02]} />
        <meshBasicMaterial color={color} wireframe transparent opacity={0.3} />
      </mesh>

      {/* Inner glow */}
      <mesh>
        <boxGeometry args={[baseScale * 0.6, baseScale * 0.6, baseScale * 0.6]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          transparent
          opacity={0.3}
        />
      </mesh>

      <Html position={[0, baseScale * 0.6, 0]} center style={{ pointerEvents: 'none' }}>
        <div style={{
          color: '#f8fafc',
          fontSize: 11,
          fontFamily: 'Inter, sans-serif',
          whiteSpace: 'nowrap',
          textShadow: '0 1px 4px rgba(0,0,0,0.9)',
          textAlign: 'center',
          userSelect: 'none',
        }}>
          <strong>{model.version.name}</strong>
          <br />
          <span style={{ fontSize: 9, opacity: 0.7 }}>{model.size.name} · {model.size.params}</span>
        </div>
      </Html>
    </group>
  )
}

// ─── Extension orbiting block ─────────────────────────────────────

function ExtensionBlock({
  extension,
  index,
  total,
}: {
  extension: Extension
  index: number
  total: number
}) {
  const ref = useRef<Group>(null!)
  const selectExtension = useStore((s) => s.selectExtension)
  const isSelected = useStore((s) => s.selectedExtensionKind === extension.kind)

  const angle = (index / total) * Math.PI * 2
  const radius = 3

  useFrame((state, delta) => {
    if (ref.current) {
      const time = state.clock.elapsedTime
      const dynamicAngle = angle + time * 0.1
      ref.current.position.x = Math.cos(dynamicAngle) * radius
      ref.current.position.z = Math.sin(dynamicAngle) * radius
      ref.current.position.y = Math.sin(time * 0.5 + index) * 0.2
      ref.current.rotation.y += delta * 0.3
    }
  })

  const color = new Color(extension.color)
  const hasSelection = extension.selectedOptionId !== null

  return (
    <group ref={ref}>
      <mesh onClick={() => selectExtension(extension.kind)}>
        <octahedronGeometry args={[hasSelection ? 0.35 : 0.25]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={isSelected ? 1.0 : 0.7}
          emissive={color}
          emissiveIntensity={isSelected ? 0.5 : hasSelection ? 0.2 : 0}
          roughness={0.4}
          metalness={0.5}
        />
      </mesh>

      <Html position={[0, 0.5, 0]} center style={{ pointerEvents: 'none' }}>
        <div style={{
          color: '#f8fafc',
          fontSize: 10,
          fontFamily: 'Inter, sans-serif',
          whiteSpace: 'nowrap',
          textShadow: '0 1px 3px rgba(0,0,0,0.8)',
          textAlign: 'center',
          userSelect: 'none',
          opacity: isSelected ? 1 : 0.7,
        }}>
          {extension.icon} {extension.label}
          {hasSelection && (
            <span style={{ display: 'block', fontSize: 8, color: extension.color, marginTop: 2 }}>
              ✓ configured
            </span>
          )}
        </div>
      </Html>
    </group>
  )
}

// ─── Cable from extension to core ─────────────────────────────────

function Cable({
  index,
  total,
  color,
}: {
  index: number
  total: number
  color: string
}) {
  const _ref = useRef<Line>(null!)
  const angle = (index / total) * Math.PI * 2
  const radius = 3

  const points = useMemo(() => {
    const pts: [number, number, number][] = []
    const steps = 20
    for (let i = 0; i <= steps; i++) {
      const t = i / steps
      const a = angle + (0.1 * 0) // static snapshot
      const ex = Math.cos(a) * radius * t
      const ez = Math.sin(a) * radius * t
      const ey = Math.sin(0.5 + index) * 0.2 * t
      pts.push([ex, ey, ez])
    }
    return pts
  }, [angle, radius, index])

  return (
    <Line
      points={points}
      color={color}
      lineWidth={1}
      transparent
      opacity={0.3}
      dashed
      dashSize={0.1}
      gapSize={0.1}
    />
  )
}

// ─── Main Canvas ──────────────────────────────────────────────────

export default function Canvas3D() {
  const selectedModel = useStore((s) => s.selectedModel)
  const extensions = useStore((s) => s.extensions)

  return (
    <div className="canvas-3d" style={{ width: '100%', height: '100%' }}>
      <Canvas gl={{ antialias: true }} dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 4, 10]} />
        <OrbitControls enableDamping dampingFactor={0.05} />

        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1.2} />
        <pointLight position={[-10, -5, -5]} intensity={0.3} color="#8b5cf6" />
        <pointLight position={[5, -10, 5]} intensity={0.3} color="#06b6d4" />

        {/* Grid */}
        <gridHelper args={[30, 30, '#1e293b', '#0f172a']} />

        {!selectedModel ? (
          <EmptyState />
        ) : (
          <>
            {/* Core engine */}
            <CoreEngine model={selectedModel} />

            {/* Extensions orbiting */}
            {extensions.map((ext, i) => (
              <ExtensionBlock
                key={ext.kind}
                extension={ext}
                index={i}
                total={extensions.length}
              />
            ))}

            {/* Cables from core to extensions */}
            {extensions.map((ext, i) => (
              <Cable
                key={`cable-${ext.kind}`}
                index={i}
                total={extensions.length}
                color={ext.color}
              />
            ))}
          </>
        )}
      </Canvas>
    </div>
  )
}
