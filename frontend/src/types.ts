// NeuroScope Visual Deep Learning Builder — Type Definitions

// ─── Model Catalog ────────────────────────────────────────────────

export type ModelFamilyId = 'cnn' | 'yolo' | 'resnet' | 'transformer' | 'gan' | 'autoencoder'

export interface ModelFamily {
  id: ModelFamilyId
  name: string
  icon: string // emoji or lucide icon name
  description: string
  versions: ModelVersion[]
}

export interface ModelVersion {
  id: string // e.g. "yolov5", "yolov8", "resnet18"
  name: string // e.g. "YOLOv5", "YOLOv8"
  sizes: ModelSize[]
}

export type ModelSizeId = 'nano' | 'small' | 'medium' | 'large' | 'xlarge'

export interface ModelSize {
  id: ModelSizeId
  name: string // "Nano", "Small", etc.
  params: string // "~3.2M", "~25M"
  description: string
  complexity: 1 | 2 | 3 | 4 | 5 // drives 3D block size
}

export interface SelectedModel {
  family: ModelFamily
  version: ModelVersion
  size: ModelSize
}

// ─── Extensions ────────────────────────────────────────────────────

export type ExtensionKind =
  | 'optimizer'
  | 'activation'
  | 'loss'
  | 'lr_scheduler'
  | 'batch_size'
  | 'epochs'
  | 'augmentation'

export interface ExtensionOption {
  id: string // e.g. "adam", "sgd", "adamw"
  name: string // "Adam"
  description: string
  whenToUse: string // plain-English guidance
  consequences: string // what happens if you pick this
  code: string // Python code snippet
}

export interface Extension {
  kind: ExtensionKind
  label: string
  icon: string
  options: ExtensionOption[]
  selectedOptionId: string | null
  position: { angle: number; distance: number } // orbit position
  color: string // visual color for cable + block
}

// ─── Workspace State ──────────────────────────────────────────────

export interface WorkspaceState {
  selectedModel: SelectedModel | null
  extensions: Extension[]
  notebookOpen: boolean
  developMode: boolean
  infoPanelCollapsed: boolean
  rightPanelTab: 'model' | 'extension' // which right panel is active
  selectedExtensionKind: ExtensionKind | null
}

// ─── Layer (for develop mode) ─────────────────────────────────────

export interface LayerInfo {
  id: string
  name: string
  type: string // "Conv2d", "BatchNorm2d", "ReLU", etc.
  params: number
  frozen: boolean
  removable: boolean
  inputShape: string
  outputShape: string
}

// ─── Export ────────────────────────────────────────────────────────

export type ExportFormat = 'ipynb' | 'yaml'

// ─── Legacy types (kept for backward compatibility) ────────────────

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

export interface Edge {
  source_id: number
  target_id: number
  edge_type: string
  label: string | null
}

export interface GraphData {
  model_id: string
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
