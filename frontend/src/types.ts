// NeuroScope TypeScript Interfaces
// Matches backend data shapes from src/graph/__init__.py and API responses

/** Single layer/operation node in the neural network graph */
export interface LayerNode {
  id: number
  name: string
  op_type: string
  category: string
  input_shapes: number[][]
  output_shapes: number[][]
  attributes: Record<string, unknown>
  params: number
  flops: number
  memory_bytes: number
  connections_in: number[]
  connections_out: number[]
  is_grouped: boolean
  grouped_types: string[]
  description: string
  display_type: string
  formatted_params: string
}

/** Connection between two layer nodes */
export interface Edge {
  source_id: number
  target_id: number
  edge_type: string // "sequential" | "skip" | "residual" | "concat"
  label: string | null
}

/** Analysis finding (warning/error/info) */
export interface Finding {
  severity: string // "CRITICAL" | "WARNING" | "INFO"
  rule_id: string
  title: string
  message: string
  fix: string
  layer_ids: number[]
  category: string
  icon: string
}

/** Complete analysis response from /api/analyze */
export interface AnalysisReport {
  success: boolean
  findings: Finding[]
  health_score: number
  health_grade: string
  critical_count: number
  warning_count: number
  info_count: number
  total_params: number
  total_flops: number
  total_memory_mb: number
  architecture_type: string
  memory_estimate: Record<string, number>
  training_time_estimate: Record<string, number>
}

/** Graph data structure (after unwrapping graph_json from upload response) */
export interface GraphData {
  model_id: string  // UUID from upload
  nodes: LayerNode[]
  edges: Edge[]
  model_name: string
  framework: string
  input_shapes: number[][]
  output_shapes: number[][]
  total_params: number
  total_flops: number
  total_memory_bytes: number
  architecture_type: string
}

/** Raw upload response from /api/upload */
export interface UploadResponse {
  success: boolean
  message: string
  model_id: string  // UUID for this upload
  model_name: string
  framework: string
  num_layers: number
  total_params: number
  graph_json: {
    nodes: LayerNode[]
    edges: Edge[]
    model_name: string
    framework: string
    input_shapes: number[][]
    output_shapes: number[][]
    total_params: number
    total_flops: number
    total_memory_bytes: number
    architecture_type: string
  }
}

/** Analyze request body */
export interface AnalyzeRequest {
  model_id: string
}
