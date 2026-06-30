import { create } from 'zustand'
import type {
  SelectedModel,
  Extension,
  ExtensionKind,
  ExportFormat,
  LayerInfo,
} from './types'

// ─── Model catalog data ───────────────────────────────────────────
import type { ModelFamily } from './types'

const MODEL_CATALOG: ModelFamily[] = [
  {
    id: 'cnn',
    name: 'CNN',
    icon: '🔲',
    description: 'Convolutional Neural Networks — great for image classification and feature extraction.',
    versions: [
      {
        id: 'cnn-basic',
        name: 'Basic CNN',
        sizes: [
          { id: 'nano', name: 'Nano', params: '~100K', description: '2 conv layers', complexity: 1 },
          { id: 'small', name: 'Small', params: '~500K', description: '4 conv layers', complexity: 2 },
          { id: 'medium', name: 'Medium', params: '~2M', description: '6 conv layers + pooling', complexity: 3 },
          { id: 'large', name: 'Large', params: '~10M', description: '8+ conv layers', complexity: 4 },
          { id: 'xlarge', name: 'X-Large', params: '~50M', description: 'Deep CNN with skip connections', complexity: 5 },
        ],
      },
    ],
  },
  {
    id: 'yolo',
    name: 'YOLO',
    icon: '👁️',
    description: 'You Only Look Once — real-time object detection models.',
    versions: [
      {
        id: 'yolov5',
        name: 'YOLOv5',
        sizes: [
          { id: 'nano', name: 'Nano', params: '~1.9M', description: 'YOLOv5n — fastest', complexity: 1 },
          { id: 'small', name: 'Small', params: '~7.2M', description: 'YOLOv5s — balanced', complexity: 2 },
          { id: 'medium', name: 'Medium', params: '~21M', description: 'YOLOv5m — accurate', complexity: 3 },
          { id: 'large', name: 'Large', params: '~46M', description: 'YOLOv5l — high accuracy', complexity: 4 },
          { id: 'xlarge', name: 'X-Large', params: '~87M', description: 'YOLOv5x — maximum accuracy', complexity: 5 },
        ],
      },
      {
        id: 'yolov8',
        name: 'YOLOv8',
        sizes: [
          { id: 'nano', name: 'Nano', params: '~3.2M', description: 'YOLOv8n', complexity: 1 },
          { id: 'small', name: 'Small', params: '~11M', description: 'YOLOv8s', complexity: 2 },
          { id: 'medium', name: 'Medium', params: '~26M', description: 'YOLOv8m', complexity: 3 },
          { id: 'large', name: 'Large', params: '~44M', description: 'YOLOv8l', complexity: 4 },
          { id: 'xlarge', name: 'X-Large', params: '~68M', description: 'YOLOv8x', complexity: 5 },
        ],
      },
    ],
  },
  {
    id: 'resnet',
    name: 'ResNet',
    icon: '🔗',
    description: 'Residual Networks — deep networks with skip connections for image recognition.',
    versions: [
      {
        id: 'resnet',
        name: 'ResNet',
        sizes: [
          { id: 'nano', name: 'ResNet-18', params: '~11M', description: '18 layers', complexity: 2 },
          { id: 'small', name: 'ResNet-34', params: '~21M', description: '34 layers', complexity: 3 },
          { id: 'medium', name: 'ResNet-50', params: '~25M', description: '50 layers with bottlenecks', complexity: 3 },
          { id: 'large', name: 'ResNet-101', params: '~44M', description: '101 layers', complexity: 4 },
          { id: 'xlarge', name: 'ResNet-152', params: '~60M', description: '152 layers', complexity: 5 },
        ],
      },
    ],
  },
  {
    id: 'transformer',
    name: 'Transformer',
    icon: '🤖',
    description: 'Attention-based architectures for NLP, vision, and multimodal tasks.',
    versions: [
      {
        id: 'vit',
        name: 'ViT',
        sizes: [
          { id: 'small', name: 'ViT-S/16', params: '~22M', description: 'Small vision transformer', complexity: 2 },
          { id: 'medium', name: 'ViT-B/16', params: '~86M', description: 'Base vision transformer', complexity: 3 },
          { id: 'large', name: 'ViT-L/16', params: '~307M', description: 'Large vision transformer', complexity: 5 },
        ],
      },
    ],
  },
  {
    id: 'gan',
    name: 'GAN',
    icon: '🎨',
    description: 'Generative Adversarial Networks — generate realistic images from noise.',
    versions: [
      {
        id: 'dcgan',
        name: 'DCGAN',
        sizes: [
          { id: 'small', name: 'Small', params: '~3M', description: '64×64 generation', complexity: 2 },
          { id: 'medium', name: 'Medium', params: '~15M', description: '128×128 generation', complexity: 3 },
          { id: 'large', name: 'Large', params: '~50M', description: '256×256 generation', complexity: 4 },
        ],
      },
    ],
  },
  {
    id: 'autoencoder',
    name: 'Autoencoder',
    icon: '🔄',
    description: 'Encode data to a compact representation and reconstruct it.',
    versions: [
      {
        id: 'vae',
        name: 'VAE',
        sizes: [
          { id: 'small', name: 'Small', params: '~1M', description: 'Latent dim 32', complexity: 1 },
          { id: 'medium', name: 'Medium', params: '~5M', description: 'Latent dim 128', complexity: 2 },
          { id: 'large', name: 'Large', params: '~20M', description: 'Latent dim 512', complexity: 3 },
        ],
      },
    ],
  },
]

// ─── Default extensions ───────────────────────────────────────────

const DEFAULT_EXTENSIONS: Extension[] = [
  {
    kind: 'optimizer',
    label: 'Optimizer',
    icon: '⚡',
    color: '#f59e0b',
    selectedOptionId: null,
    position: { angle: 0, distance: 3 },
    options: [
      {
        id: 'adam',
        name: 'Adam',
        description: 'Adaptive learning rate optimizer — the most popular choice.',
        whenToUse: 'Default choice for most tasks. Works well out of the box.',
        consequences: 'Slightly higher memory usage due to momentum tracking.',
        code: 'optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)',
      },
      {
        id: 'sgd',
        name: 'SGD + Momentum',
        description: 'Stochastic Gradient Descent with momentum.',
        whenToUse: 'When you want fine control and often better generalization.',
        consequences: 'Requires careful learning rate tuning. Slower to converge.',
        code: 'optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)',
      },
      {
        id: 'adamw',
        name: 'AdamW',
        description: 'Adam with decoupled weight decay — better regularization.',
        whenToUse: 'Training transformers or when weight decay matters.',
        consequences: 'Slightly different regularization behavior than Adam.',
        code: 'optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)',
      },
    ],
  },
  {
    kind: 'activation',
    label: 'Activation',
    icon: '📈',
    color: '#8b5cf6',
    selectedOptionId: null,
    position: { angle: 51, distance: 3 },
    options: [
      {
        id: 'relu',
        name: 'ReLU',
        description: 'Rectified Linear Unit — simple and effective.',
        whenToUse: 'Default for hidden layers in most networks.',
        consequences: 'Can cause "dead neurons" where gradients are zero.',
        code: 'activation = nn.ReLU()',
      },
      {
        id: 'gelu',
        name: 'GELU',
        description: 'Gaussian Error Linear Unit — smooth approximation of ReLU.',
        whenToUse: 'Standard in transformers and modern architectures.',
        consequences: 'Slightly more compute than ReLU.',
        code: 'activation = nn.GELU()',
      },
      {
        id: 'silu',
        name: 'SiLU / Swish',
        description: 'Sigmoid Linear Unit — self-gated activation.',
        whenToUse: 'Used in EfficientNet, YOLOv5+. Smooth gradients.',
        consequences: 'More compute per activation.',
        code: 'activation = nn.SiLU()',
      },
      {
        id: 'leaky_relu',
        name: 'Leaky ReLU',
        description: 'Allows small negative gradients to flow.',
        whenToUse: 'When you observe dead neurons with standard ReLU.',
        consequences: 'One extra hyperparameter (negative slope).',
        code: 'activation = nn.LeakyReLU(0.01)',
      },
    ],
  },
  {
    kind: 'loss',
    label: 'Loss Function',
    icon: '🎯',
    color: '#ef4444',
    selectedOptionId: null,
    position: { angle: 102, distance: 3 },
    options: [
      {
        id: 'cross_entropy',
        name: 'Cross Entropy',
        description: 'Standard classification loss combining LogSoftmax + NLLLoss.',
        whenToUse: 'Multi-class classification tasks.',
        consequences: 'Sensitive to class imbalance — consider class weights.',
        code: 'criterion = nn.CrossEntropyLoss()',
      },
      {
        id: 'mse',
        name: 'MSE Loss',
        description: 'Mean Squared Error — measures average squared difference.',
        whenToUse: 'Regression tasks or when outputs are continuous.',
        consequences: 'Sensitive to outliers. Not suitable for classification.',
        code: 'criterion = nn.MSELoss()',
      },
      {
        id: 'bce',
        name: 'BCE With Logits',
        description: 'Binary Cross Entropy with built-in sigmoid.',
        whenToUse: 'Multi-label classification or binary classification.',
        consequences: 'Each output is independent — no mutual exclusivity.',
        code: 'criterion = nn.BCEWithLogitsLoss()',
      },
      {
        id: 'focal',
        name: 'Focal Loss',
        description: 'Down-weights easy examples, focuses on hard ones.',
        whenToUse: 'Highly imbalanced datasets (e.g., object detection).',
        consequences: 'Extra hyperparameters (alpha, gamma) to tune.',
        code: 'criterion = FocalLoss(alpha=0.25, gamma=2.0)',
      },
    ],
  },
  {
    kind: 'lr_scheduler',
    label: 'LR Scheduler',
    icon: '📉',
    color: '#06b6d4',
    selectedOptionId: null,
    position: { angle: 153, distance: 3 },
    options: [
      {
        id: 'cosine',
        name: 'Cosine Annealing',
        description: 'Smoothly decays LR following a cosine curve.',
        whenToUse: 'Most training runs — provides smooth convergence.',
        consequences: 'LR goes to near zero at end. Good with warm restarts.',
        code: 'scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)',
      },
      {
        id: 'step',
        name: 'Step LR',
        description: 'Decays LR by a factor every N epochs.',
        whenToUse: 'When you know when to reduce LR (e.g., after plateau).',
        consequences: 'Abrust LR changes can cause loss spikes.',
        code: 'scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)',
      },
      {
        id: 'plateau',
        name: 'Reduce On Plateau',
        description: 'Reduces LR when a metric stops improving.',
        whenToUse: 'When monitoring validation loss and want adaptive reduction.',
        consequences: 'Requires metric monitoring. Can be too conservative.',
        code: 'scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)',
      },
    ],
  },
  {
    kind: 'batch_size',
    label: 'Batch Size',
    icon: '📦',
    color: '#10b981',
    selectedOptionId: null,
    position: { angle: 204, distance: 3 },
    options: [
      {
        id: 'bs_16',
        name: '16',
        description: 'Small batch — lower memory, noisier gradients.',
        whenToUse: 'Limited GPU memory or very large models.',
        consequences: 'Noisier gradients can help generalization but slow convergence.',
        code: 'train_loader = DataLoader(dataset, batch_size=16, shuffle=True)',
      },
      {
        id: 'bs_32',
        name: '32',
        description: 'Standard batch size for most training.',
        whenToUse: 'Good default for most image classification tasks.',
        consequences: 'Balanced trade-off between speed and memory.',
        code: 'train_loader = DataLoader(dataset, batch_size=32, shuffle=True)',
      },
      {
        id: 'bs_64',
        name: '64',
        description: 'Larger batch — faster training, needs more memory.',
        whenToUse: 'When GPU memory allows and you want faster epochs.',
        consequences: 'May need higher learning rate. Can generalize worse.',
        code: 'train_loader = DataLoader(dataset, batch_size=64, shuffle=True)',
      },
      {
        id: 'bs_128',
        name: '128',
        description: 'Large batch — very fast but memory hungry.',
        whenToUse: 'Multi-GPU setups or small models with enough VRAM.',
        consequences: 'Requires learning rate scaling. Risk of sharp minima.',
        code: 'train_loader = DataLoader(dataset, batch_size=128, shuffle=True)',
      },
    ],
  },
  {
    kind: 'epochs',
    label: 'Epochs',
    icon: '🔁',
    color: '#f97316',
    selectedOptionId: null,
    position: { angle: 255, distance: 3 },
    options: [
      {
        id: 'ep_10',
        name: '10',
        description: 'Quick experiment — see if the model learns anything.',
        whenToUse: 'Prototyping or testing your pipeline.',
        consequences: 'Likely underfitting. Good for smoke tests.',
        code: 'num_epochs = 10',
      },
      {
        id: 'ep_50',
        name: '50',
        description: 'Standard training run.',
        whenToUse: 'Most tasks with moderate dataset size.',
        consequences: 'Usually sufficient with proper LR scheduling.',
        code: 'num_epochs = 50',
      },
      {
        id: 'ep_100',
        name: '100',
        description: 'Extended training for better convergence.',
        whenToUse: 'Large datasets or when 50 epochs isn\'t enough.',
        consequences: 'Longer training time. Use early stopping to avoid overfitting.',
        code: 'num_epochs = 100',
      },
      {
        id: 'ep_300',
        name: '300',
        description: 'Full training schedule (like ImageNet training).',
        whenToUse: 'Benchmark results or when maximum performance is needed.',
        consequences: 'Very long training. Use checkpointing and early stopping.',
        code: 'num_epochs = 300',
      },
    ],
  },
  {
    kind: 'augmentation',
    label: 'Augmentation',
    icon: '🔀',
    color: '#ec4899',
    selectedOptionId: null,
    position: { angle: 306, distance: 3 },
    options: [
      {
        id: 'none',
        name: 'None',
        description: 'No augmentation — use raw data as-is.',
        whenToUse: 'Data is already diverse or augmentation doesn\'t apply.',
        consequences: 'May overfit on small datasets.',
        code: '# No augmentation applied',
      },
      {
        id: 'basic',
        name: 'Basic',
        description: 'Random horizontal flip + small rotation.',
        whenToUse: 'Good default for image classification.',
        consequences: 'Slight improvement in generalization with minimal overhead.',
        code: 'transform = transforms.Compose([\n  transforms.RandomHorizontalFlip(),\n  transforms.RandomRotation(10),\n])',
      },
      {
        id: 'advanced',
        name: 'Advanced (AutoAugment)',
        description: 'Learned augmentation policies — CutOut, MixUp, etc.',
        whenToUse: 'When you need maximum generalization on limited data.',
        consequences: 'Slower data loading. Can hurt if data is already diverse.',
        code: 'transform = transforms.Compose([\n  transforms.AutoAugment(),\n  transforms.RandomErasing(p=0.5),\n])',
      },
    ],
  },
]

// ─── Store interface ──────────────────────────────────────────────

interface NeuroScopeState {
  // Model catalog
  modelCatalog: ModelFamily[]

  // Selection
  selectedModel: SelectedModel | null
  extensions: Extension[]
  selectedExtensionKind: ExtensionKind | null

  // UI
  notebookOpen: boolean
  developMode: boolean
  infoPanelCollapsed: boolean
  rightPanelTab: 'model' | 'extension'

  // Develop mode layers
  layers: LayerInfo[]

  // Actions
  selectModel: (model: SelectedModel) => void
  clearModel: () => void
  selectExtension: (kind: ExtensionKind) => void
  updateExtensionOption: (kind: ExtensionKind, optionId: string) => void
  toggleNotebook: () => void
  toggleDevelopMode: () => void
  toggleInfoPanel: () => void
  setRightPanelTab: (tab: 'model' | 'extension') => void
  toggleLayerFrozen: (layerId: string) => void
  removeLayer: (layerId: string) => void
  addLayer: (afterId: string, layerType: string) => void
  exportNotebook: (format: ExportFormat) => string
  reset: () => void
}

// ─── Store ────────────────────────────────────────────────────────

export const useStore = create<NeuroScopeState>((set, get) => ({
  modelCatalog: MODEL_CATALOG,

  selectedModel: null,
  extensions: DEFAULT_EXTENSIONS.map((e) => ({ ...e })),
  selectedExtensionKind: null,

  notebookOpen: false,
  developMode: false,
  infoPanelCollapsed: false,
  rightPanelTab: 'model',

  layers: [],

  selectModel: (model) => {
    const complexity = model.size.complexity
    // Generate layers based on model complexity
    const layerTypes = [
      { type: 'Conv2d', base: 64 },
      { type: 'BatchNorm2d', base: 0 },
      { type: 'ReLU', base: 0 },
      { type: 'MaxPool2d', base: 0 },
    ]
    const layers: LayerInfo[] = []
    let layerIdx = 0
    for (let block = 0; block < complexity + 1; block++) {
      const outChannels = layerTypes[0].base * (block + 1)
      layers.push({
        id: `layer-${layerIdx}`,
        name: `Conv2d_${block}`,
        type: 'Conv2d',
        params: outChannels * 3 * 3 * 3,
        frozen: false,
        removable: block > 0,
        inputShape: `[B, ${block === 0 ? 3 : layerTypes[0].base * block}, H, W]`,
        outputShape: `[B, ${outChannels}, H, W]`,
      })
      layerIdx++
      layers.push({
        id: `layer-${layerIdx}`,
        name: `BN_${block}`,
        type: 'BatchNorm2d',
        params: outChannels * 2,
        frozen: false,
        removable: true,
        inputShape: `[B, ${outChannels}, H, W]`,
        outputShape: `[B, ${outChannels}, H, W]`,
      })
      layerIdx++
      layers.push({
        id: `layer-${layerIdx}`,
        name: `ReLU_${block}`,
        type: 'ReLU',
        params: 0,
        frozen: false,
        removable: true,
        inputShape: `[B, ${outChannels}, H, W]`,
        outputShape: `[B, ${outChannels}, H, W]`,
      })
      layerIdx++
      if (block < complexity) {
        layers.push({
          id: `layer-${layerIdx}`,
        name: `Pool_${block}`,
        type: 'MaxPool2d',
        params: 0,
        frozen: false,
        removable: true,
        inputShape: `[B, ${outChannels}, H, W]`,
        outputShape: `[B, ${outChannels}, H/2, W/2]`,
        })
        layerIdx++
      }
    }
    // Add FC layers
    const lastChannels = layerTypes[0].base * (complexity + 1)
    layers.push({
      id: `layer-${layerIdx}`,
      name: 'Flatten',
      type: 'Flatten',
      params: 0,
      frozen: false,
      removable: false,
      inputShape: `[B, ${lastChannels}, 1, 1]`,
      outputShape: `[B, ${lastChannels}]`,
    })
    layerIdx++
    layers.push({
      id: `layer-${layerIdx}`,
      name: 'FC_out',
      type: 'Linear',
      params: lastChannels * 10,
      frozen: false,
      removable: false,
      inputShape: `[B, ${lastChannels}]`,
      outputShape: '[B, 10]',
    })

    set({
      selectedModel: model,
      layers,
      rightPanelTab: 'model',
      notebookOpen: true,
    })
  },

  clearModel: () =>
    set({
      selectedModel: null,
      layers: [],
      extensions: DEFAULT_EXTENSIONS.map((e) => ({ ...e, selectedOptionId: null })),
      selectedExtensionKind: null,
      notebookOpen: false,
      developMode: false,
      rightPanelTab: 'model',
    }),

  selectExtension: (kind) =>
    set({
      selectedExtensionKind: kind,
      rightPanelTab: 'extension',
    }),

  updateExtensionOption: (kind, optionId) =>
    set((state) => ({
      extensions: state.extensions.map((ext) =>
        ext.kind === kind ? { ...ext, selectedOptionId: optionId } : ext
      ),
      notebookOpen: true,
    })),

  toggleNotebook: () => set((state) => ({ notebookOpen: !state.notebookOpen })),

  toggleDevelopMode: () =>
    set((state) => ({ developMode: !state.developMode })),

  toggleInfoPanel: () =>
    set((state) => ({ infoPanelCollapsed: !state.infoPanelCollapsed })),

  setRightPanelTab: (tab) => set({ rightPanelTab: tab }),

  toggleLayerFrozen: (layerId) =>
    set((state) => ({
      layers: state.layers.map((l) =>
        l.id === layerId ? { ...l, frozen: !l.frozen } : l
      ),
    })),

  removeLayer: (layerId) =>
    set((state) => ({
      layers: state.layers.filter((l) => l.id !== layerId),
    })),

  addLayer: (afterId, layerType) =>
    set((state) => {
      const idx = state.layers.findIndex((l) => l.id === afterId)
      if (idx === -1) return state
      const after = state.layers[idx]
      const newId = `layer-${Date.now()}`
      const newLayer: LayerInfo = {
        id: newId,
        name: `${layerType}_${newId.slice(-4)}`,
        type: layerType,
        params: layerType === 'Conv2d' ? 1728 : layerType === 'Linear' ? 640 : 0,
        frozen: false,
        removable: true,
        inputShape: after.outputShape,
        outputShape: after.outputShape,
      }
      const layers = [...state.layers]
      layers.splice(idx + 1, 0, newLayer)
      return { layers }
    }),

  exportNotebook: (format) => {
    const state = get()
    const model = state.selectedModel
    if (!model) return ''

    if (format === 'yaml') {
      const lines = [
        '# NeuroScope Model Configuration',
        `# Generated: ${new Date().toISOString()}`,
        '',
        'model:',
        `  family: ${model.family.id}`,
        `  version: ${model.version.id}`,
        `  size: ${model.size.id}`,
        `  name: "${model.version.name} ${model.size.name}"`,
        `  params: "${model.size.params}"`,
        '',
        'extensions:',
      ]
      for (const ext of state.extensions) {
        if (ext.selectedOptionId) {
          const opt = ext.options.find((o) => o.id === ext.selectedOptionId)
          lines.push(`  ${ext.kind}: ${opt?.id || 'none'}`)
        }
      }
      return lines.join('\n')
    }

    // ipynb format
    const cells: object[] = []
    cells.push({
      cell_type: 'markdown',
      source: [
        `# ${model.version.name} ${model.size.name}\n`,
        `**Family:** ${model.family.name} | **Params:** ${model.size.params}\n`,
        `> ${model.size.description}`,
      ],
    })
    cells.push({
      cell_type: 'code',
      source: ['import torch', 'import torch.nn as nn', 'import torch.optim as optim', ''],
    })

    for (const ext of state.extensions) {
      if (ext.selectedOptionId) {
        const opt = ext.options.find((o) => o.id === ext.selectedOptionId)
        if (opt) {
          cells.push({
            cell_type: 'markdown',
            source: [`## ${ext.label}: ${opt.name}\n`, `${opt.description}\n`, `**When to use:** ${opt.whenToUse}`],
          })
          cells.push({
            cell_type: 'code',
            source: [opt.code, ''],
          })
        }
      }
    }

    const nb = {
      nbformat: 4,
      nbformat_minor: 5,
      metadata: {
        kernelspec: { display_name: 'Python 3', language: 'python', name: 'python3' },
        language_info: { name: 'python', version: '3.10.0' },
      },
      cells,
    }
    return JSON.stringify(nb, null, 2)
  },

  reset: () =>
    set({
      selectedModel: null,
      extensions: DEFAULT_EXTENSIONS.map((e) => ({ ...e, selectedOptionId: null })),
      selectedExtensionKind: null,
      notebookOpen: false,
      developMode: false,
      infoPanelCollapsed: false,
      rightPanelTab: 'model',
      layers: [],
    }),
}))
