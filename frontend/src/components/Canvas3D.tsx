import { useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Html, Line } from '@react-three/drei'
import { Color, Vector3 } from 'three'
import type { GraphData, LayerNode } from '../types'

interface Canvas3DProps {
  graphData: GraphData
  onLayerClick: (layer: LayerNode) => void
}

// Layer type → 3D shape + color mapping
const LAYER_STYLES: Record<string, { color: string; geometry: string }> = {
  convolution: { color: '#6366f1', geometry: 'box' },
  linear: { color: '#8b5cf6', geometry: 'plane' },
  pooling: { color: '#06b6d4', geometry: 'small_cube' },
  activation: { color: '#f59e0b', geometry: 'sphere' },
  normalization: { color: '#10b981', geometry: 'slab' },
  reshape: { color: '#ec4899', geometry: 'cone' },
  regularization: { color: '#ef4444', geometry: 'wireframe' },
  recurrent: { color: '#14b8a6', geometry: 'cylinder' },
  attention: { color: '#f97316', geometry: 'octahedron' },
  combination: { color: '#84cc16', geometry: 'merge' },
}

function LayerMesh({ node, position, onClick }: {
  node: LayerNode
  position: [number, number, number]
  onClick: (layer: LayerNode) => void
}) {
  const style = LAYER_STYLES[node.category] || { color: '#64748b', geometry: 'box' }
  const color = new Color(style.color)

  const getGeometry = () => {
    switch (style.geometry) {
      case 'sphere':
        return <sphereGeometry args={[0.4, 16, 16]} />
      case 'cylinder':
        return <cylinderGeometry args={[0.3, 0.3, 0.8, 16]} />
      case 'cone':
        return <coneGeometry args={[0.3, 0.8, 16]} />
      case 'octahedron':
        return <octahedronGeometry args={[0.4]} />
      case 'plane':
        return <boxGeometry args={[1.2, 0.1, 0.8]} />
      case 'small_cube':
        return <boxGeometry args={[0.4, 0.4, 0.4]} />
      case 'slab':
        return <boxGeometry args={[1.0, 0.1, 0.6]} />
      default:
        return <boxGeometry args={[0.8, 0.8, 0.8]} />
    }
  }

  return (
    <group position={position}>
      <mesh onClick={() => onClick(node)}>
        {getGeometry()}
        <meshStandardMaterial color={color} transparent opacity={0.85} />
      </mesh>
      <Html position={[0, 0.8, 0]} center style={{ pointerEvents: 'none' }}>
        <div style={{
          color: '#f8fafc',
          fontSize: 10,
          fontFamily: 'Inter, sans-serif',
          whiteSpace: 'nowrap',
          textShadow: '0 1px 3px rgba(0,0,0,0.8)',
          textAlign: 'center',
          userSelect: 'none',
        }}>
          {node.display_type}
        </div>
      </Html>
    </group>
  )
}

function EdgeLine({ start, end, edgeType }: {
  start: [number, number, number]
  end: [number, number, number]
  edgeType: string
}) {
  const color = edgeType === 'residual' ? '#10b981' :
                edgeType === 'skip' ? '#f59e0b' : '#94a3b8'

  // For skip/residual connections, draw a curved line
  const points = useMemo(() => {
    const s = new Vector3(...start)
    const e = new Vector3(...end)
    if (edgeType === 'skip' || edgeType === 'residual') {
      // Arc upward for skip connections
      const mid = new Vector3().lerpVectors(s, e, 0.5)
      mid.y += 2.0
      const curvePoints: [number, number, number][] = []
      for (let t = 0; t <= 1; t += 0.1) {
        const p = new Vector3()
        // Quadratic bezier
        const mt = 1 - t
        p.x = mt * mt * s.x + 2 * mt * t * mid.x + t * t * e.x
        p.y = mt * mt * s.y + 2 * mt * t * mid.y + t * t * e.y
        p.z = mt * mt * s.z + 2 * mt * t * mid.z + t * t * e.z
        curvePoints.push([p.x, p.y, p.z])
      }
      curvePoints.push(end)
      return curvePoints
    }
    return [start, end]
  }, [start[0], start[1], start[2], end[0], end[1], end[2], edgeType])

  return (
    <Line
      points={points}
      color={color}
      lineWidth={1.5}
      dashed={edgeType === 'skip'}
    />
  )
}

export default function Canvas3D({ graphData, onLayerClick }: Canvas3DProps) {
  const nodes = graphData?.nodes || []
  const edges = graphData?.edges || []

  // Calculate node positions (simple horizontal layout)
  const nodePositions: Record<number, [number, number, number]> = {}
  const spacing = 2.5
  nodes.forEach((node, i) => {
    nodePositions[node.id] = [i * spacing - (nodes.length * spacing) / 2, 0, 0]
  })

  return (
    <div className="canvas-3d" style={{ width: '100%', height: '100%' }}>
      <Canvas gl={{ antialias: true }} dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 5, 15]} />
        <OrbitControls enableDamping dampingFactor={0.05} />

        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />

        {/* Grid */}
        <gridHelper args={[50, 50, '#334155', '#1e293b']} />

        {/* Layers */}
        {nodes.map((node) => (
          <LayerMesh
            key={node.id}
            node={node}
            position={nodePositions[node.id]}
            onClick={onLayerClick}
          />
        ))}

        {/* Edges */}
        {edges.map((edge, i) => {
          const start = nodePositions[edge.source_id]
          const end = nodePositions[edge.target_id]
          if (!start || !end) return null
          return (
            <EdgeLine
              key={i}
              start={[start[0] + 0.4, start[1], start[2]]}
              end={[end[0] - 0.4, end[1], end[2]]}
              edgeType={edge.edge_type}
            />
          )
        })}
      </Canvas>
    </div>
  )
}
