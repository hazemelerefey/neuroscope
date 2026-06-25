import { create } from 'zustand'
import type { GraphData, AnalysisReport, LayerNode } from './types'

interface NeuroScopeState {
  // Data
  graphData: GraphData | null
  analysisData: AnalysisReport | null
  selectedLayer: LayerNode | null

  // UI state
  isUploading: boolean
  error: string | null

  // Actions
  setGraphData: (data: GraphData) => void
  setAnalysisData: (data: AnalysisReport) => void
  selectLayer: (layer: LayerNode | null) => void
  setUploading: (v: boolean) => void
  setError: (e: string | null) => void
  reset: () => void
}

export const useStore = create<NeuroScopeState>((set) => ({
  graphData: null,
  analysisData: null,
  selectedLayer: null,
  isUploading: false,
  error: null,

  setGraphData: (data) => set({ graphData: data, error: null }),
  setAnalysisData: (data) => set({ analysisData: data }),
  selectLayer: (layer) => set({ selectedLayer: layer }),
  setUploading: (v) => set({ isUploading: v }),
  setError: (e) => set({ error: e }),
  reset: () =>
    set({
      graphData: null,
      analysisData: null,
      selectedLayer: null,
      isUploading: false,
      error: null,
    }),
}))
