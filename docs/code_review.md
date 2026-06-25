# NeuroScope Code Review Report

**Date:** 2026-06-25  
**Reviewer:** Senior Python Code Reviewer  
**Scope:** All Python source files in `src/` and `tests/`  

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical Bugs | 4 |
| 🟠 Functional Issues | 5 |
| 🟡 Code Quality | 7 |
| 🔵 Test Issues | 4 |
| **Total** | **20** |

---

## 🔴 Critical Bugs

### BUG-01: Upload and Analyze use separate `graph_store` — analyze always returns 404

**File:** `src/api/routes/upload.py` and `src/api/routes/analyze.py`

**Problem:**  
`upload.py` parses the model into a `NeuroScopeGraph` and serializes it to JSON for the response, but **never stores the graph object** in any shared store. Meanwhile, `analyze.py` defines its own `graph_store: dict[str, NeuroScopeGraph] = {}` (line 16) and looks up graphs by `model_id`. Since nothing ever populates this dict, every `/analyze` request returns 404.

**Fix (in `src/api/routes/upload.py`):**

```python
# Add import at top
from src.api.routes.analyze import graph_store

# In upload_model(), after graph = _parse_model(tmp_path):
# Store the graph for later analysis
graph_id = os.path.splitext(filename)[0]  # or use a UUID
graph_store[graph_id] = graph

# Update UploadResponse to include the model_id
return UploadResponse(
    success=True,
    message=f"Successfully parsed {filename}",
    model_id=graph_id,  # Add this field
    model_name=graph.model_name,
    ...
)
```

Or better: move `graph_store` to a shared module (e.g., `src/api/store.py`) and import from both routes.

---

### BUG-02: `_matmul_flops` double-counts batch dimension for 2D inputs

**File:** `src/analysis/flops.py`, lines 79–86

**Problem:**  
For a 2D input `[M, K]` → `[M, N]`, the function sets both `batch = M` (line 81) and `m = M` (line 83, else branch), resulting in FLOPs = `2 * M * M * K * N` instead of `2 * M * K * N`.

```python
def _matmul_flops(input_shape: list, output_shape: list) -> int:
    if len(input_shape) < 2 or len(output_shape) < 2:
        return 0
    batch = input_shape[0] if len(input_shape) > 1 else 1      # M for 2D
    m = input_shape[-2] if len(input_shape) > 2 else input_shape[0]  # also M for 2D
    k = input_shape[-1]
    n = output_shape[-1]
    return 2 * batch * m * k * n  # 2 * M * M * K * N — WRONG
```

The test passes by coincidence because `input_shapes=[[1, 512]]` has `M=1`, so `batch*m = 1*1 = 1`.

**Fix:**

```python
def _matmul_flops(input_shape: list, output_shape: list) -> int:
    """FLOPs for matrix multiplication: 2 × batch × M × K × N"""
    if len(input_shape) < 2 or len(output_shape) < 2:
        return 0

    if len(input_shape) >= 3:
        # Batched: [batch, seq, hidden]
        batch = input_shape[0]
        m = input_shape[-2]
    else:
        # 2D: [M, K] — M serves as both batch and rows
        batch = 1
        m = input_shape[0]

    k = input_shape[-1]
    n = output_shape[-1]
    return 2 * batch * m * k * n
```

**Also update test** to cover non-trivial batch:

```python
def test_matmul_flops_2d(self):
    """MatMul with 2D input should not double-count."""
    node = _make_node(
        0, "MatMul",
        input_shapes=[[32, 512]],
        output_shapes=[[32, 256]],
    )
    flops = _calculate_layer_flops(node)
    assert flops == 2 * 32 * 512 * 256  # NOT 2 * 32 * 32 * 512 * 256
```

---

### BUG-03: `_check_no_pooling` stride detection is broken — always bypassed for 2D convolutions

**File:** `src/analysis/rules/efficiency_rules.py`, lines 93–97

**Problem:**  
The code checks `n.attributes.get("strides", [1]) != [1]` to detect strided convolutions. But ONNX stores strides as `[1, 1]` for 2D convolutions. Since `[1, 1] != [1]` is `True`, **every 2D convolution is incorrectly detected as strided**, causing the rule to never fire even when there's genuinely no downsampling.

```python
has_strided_conv = any(
    n.attributes.get("strides", [1]) != [1]  # BUG: [1,1] != [1] is True
    for n in graph.nodes
    if n.op_type in CONV_OPS
)
```

**Fix:**

```python
has_strided_conv = any(
    any(s > 1 for s in n.attributes.get("strides", [1, 1]))
    for n in graph.nodes
    if n.op_type in CONV_OPS
)
```

---

### BUG-04: Missing import of `BaseParser` in test

**File:** `tests/test_parsers/test_onnx_parser.py`, line 24

**Problem:**  
`test_detect_format` calls `BaseParser.detect_format(...)` but `BaseParser` is never imported. This test will raise `NameError: name 'BaseParser' is not defined`.

```python
# Line 24
def test_detect_format(self):
    assert BaseParser.detect_format("model.onnx") == "onnx"  # NameError!
```

**Fix:**

```python
from src.parsers.onnx_parser import ONNXParser
from src.parsers import BaseParser  # Add this import
from src.graph import NeuroScopeGraph
```

---

## 🟠 Functional Issues

### FUNC-01: ONNX parser does not populate `connections_in` / `connections_out` on nodes

**File:** `src/parsers/onnx_parser.py`, `parse()` method

**Problem:**  
`LayerNode` has `connections_in` and `connections_out` fields that are serialized by `upload.py`'s `_serialize_graph()`. But the ONNX parser builds edges separately and never populates these fields on the node objects. The frontend will always receive empty lists for connection data on each node.

**Fix (in `src/parsers/onnx_parser.py`, after building edges):**

```python
# After: edges = self._build_edges(graph_proto, tensor_producers)
# Populate connections_in and connections_out on nodes
for edge in edges:
    if edge.source_id < len(nodes):
        nodes[edge.source_id].connections_out.append(edge.target_id)
    if edge.target_id < len(nodes):
        nodes[edge.target_id].connections_in.append(edge.source_id)
```

---

### FUNC-02: Upload route deletes temp file twice (potential error)

**File:** `src/api/routes/upload.py`, lines 63–72

**Problem:**  
The `finally` block calls `os.unlink(tmp_path)`, but the `except` block on line 68 also calls `os.unlink(tmp_path)`. On the success path, the `finally` block deletes the file. On the error path, the `except` block deletes it first, then `finally` tries again — raising `FileNotFoundError`.

```python
except Exception as e:
    os.unlink(tmp_path)           # First delete
    raise HTTPException(...)
finally:
    if os.path.exists(tmp_path):  # Guard exists but race condition possible
        os.unlink(tmp_path)       # Second delete
```

**Fix:** Remove the `os.unlink` from the `except` block; the `finally` block handles cleanup:

```python
except Exception as e:
    raise HTTPException(status_code=422, detail=f"Failed to parse model: {e}")
finally:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
```

---

### FUNC-03: Compare endpoint is a stub

**File:** `src/api/routes/compare.py`

**Problem:**  
The entire compare feature is unimplemented. The endpoint always returns `success=False` with a placeholder message. If this is intentional for Phase 3, it should be documented. If not, this is a missing implementation.

**Recommendation:** Either implement or raise `HTTPException(501)` with a clear "Not Implemented" status code so clients can distinguish it from a failure:

```python
from fastapi import HTTPException

@router.post("/compare", response_model=CompareResponse)
async def compare_models(request: CompareRequest):
    raise HTTPException(
        status_code=501,
        detail="Model comparison not yet implemented. Coming in Phase 3.",
    )
```

---

### FUNC-04: Export endpoint only supports 2 of 5 documented formats

**File:** `src/api/routes/export.py`

**Problem:**  
The docstring and `ExportRequest` model document 5 formats (`glb`, `svg`, `pdf`, `markdown`, `html`), but only `markdown` and `html` are implemented. Requests for `glb`, `svg`, or `pdf` get a 400 error. This is misleading API documentation.

**Fix:** Update the docstring to reflect current state, or implement the missing formats:

```python
class ExportRequest(BaseModel):
    model_id: str
    format: str  # Currently supported: "markdown", "html"
```

---

### FUNC-05: `json` imported but unused in export.py

**File:** `src/api/routes/export.py`, line 9

**Problem:**  
`import json` is present but never used.

**Fix:** Remove the unused import.

---

## 🟡 Code Quality Issues

### QUAL-01: `_check_missing_activation` uses fragile `graph.nodes.index()` instead of loop variable

**File:** `src/analysis/rules/layer_rules.py`, lines 68–74

**Problem:**  
The inner loop computes `graph.nodes.index(next_node)` to find the position of `next_node`, but `next_node` is already `nodes[i + 1]`. The `index()` call does a linear search and will return the **first** occurrence if there are duplicate objects, which could produce an incorrect range. Should use `i + 1` directly.

```python
for j in range(i + 1, graph.nodes.index(next_node)):  # Fragile
```

**Fix:**

```python
for j in range(i + 1, i + 1):  # This is always empty for adjacent nodes
    ...
```

Wait — for adjacent nodes (which is the only case we check since outer loop is `range(len-1)`), the range is always empty, so `has_activation_between` is always `False`. This means the check only flags adjacent linear/conv pairs, which is correct. But the code is confusing. Simplify:

```python
def _check_missing_activation(self, graph: NeuroScopeGraph) -> list[Finding]:
    """Check for linear/conv layers without activation between them."""
    findings = []
    nodes = graph.nodes

    for i in range(len(nodes) - 1):
        current = nodes[i]
        next_node = nodes[i + 1]

        if (
            current.op_type in (LINEAR_OPS | CONV_OPS)
            and next_node.op_type in (LINEAR_OPS | CONV_OPS)
        ):
            findings.append(
                Finding(
                    severity="CRITICAL",
                    rule_id="LAYER_001",
                    title="Missing Activation Function",
                    message=(
                        f"No activation between '{current.name}' ({current.op_type}) "
                        f"and '{next_node.name}' ({next_node.op_type}). "
                        f"Stacking linear layers without activation collapses to a "
                        f"single linear transformation."
                    ),
                    fix="Add ReLU, GELU, or SiLU activation between the layers.",
                    layer_ids=[current.id, next_node.id],
                    category="layer",
                )
            )

    return findings
```

---

### QUAL-02: Set union with `|` operator on plain sets — Python 3.9+ only

**File:** `src/analysis/rules/layer_rules.py`, lines 54, 55, 108, 128

**Problem:**  
`LINEAR_OPS | CONV_OPS` uses the `|` operator for set union. While this works in Python 3.9+, it's less explicit and may confuse readers. For clarity and compatibility, use `.union()` or combine at definition time.

**Fix:** Define combined sets at module level:

```python
LINEAR_CONV_OPS = LINEAR_OPS | CONV_OPS  # At module level is fine
```

Then use `LINEAR_CONV_OPS` in the checks.

---

### QUAL-03: `_check_premature_flatten` relies on sequential node ordering

**File:** `src/analysis/rules/architecture_rules.py`, lines 107–123

**Problem:**  
The check iterates `graph.nodes[i + 1:]` looking for Conv ops after a Flatten. But the node list may not reflect actual execution order (depends on parser). Should check via edges/topological order for correctness.

**Recommendation:** This is acceptable for the current ONNX parser (which preserves protobuf order), but add a comment:

```python
# NOTE: Assumes nodes are in topological/execution order.
# This holds for ONNX but may need revisiting for other parsers.
```

---

### QUAL-04: `estimate_memory` creates intermediate list for activation shapes

**File:** `src/analysis/memory.py`, lines 62–69

**Problem:**  
The activation memory loop creates `act_shape` as a new list for each node. Minor inefficiency, but more importantly, if `shape` has dynamic dimensions (`-1`), the `all(s > 0 for s in shape)` guard correctly skips them, but there's no logging/warning about skipped layers.

**Fix (minor):** Add a comment or warning:

```python
# Note: Dynamic dimensions (-1) cause this layer to be skipped
if shape and all(s > 0 for s in shape):
    ...
```

---

### QUAL-05: `LayerRules._check_sigmoid_in_deep_network` iterates all nodes including activations

**File:** `src/analysis/rules/layer_rules.py`, line 93

**Problem:**  
The depth counter excludes activations/utility/reshape, which is correct. But the loop at line 93 iterates `graph.nodes` and checks for `SATURATING_ACTIVATIONS`. If there's a Sigmoid as the **output layer** of a classification network, it would be flagged — which may not be a real issue.

**Recommendation:** Add a check to skip the last activation if it's the final output:

```python
for node in graph.nodes[:-1]:  # Skip last node (likely output activation)
    if node.op_type in SATURATING_ACTIVATIONS:
        ...
```

---

### QUAL-06: ONNX parser silently swallows shape inference errors

**File:** `src/parsers/onnx_parser.py`, lines 123–126

**Problem:**
```python
if infer_shapes:
    try:
        model = shape_inference.infer_shapes(model)
    except Exception:
        pass  # Continue without shape inference
```

Catching all exceptions silently makes debugging difficult. At minimum, log a warning.

**Fix:**
```python
import logging
logger = logging.getLogger(__name__)

try:
    model = shape_inference.infer_shapes(model)
except Exception as e:
    logger.warning("Shape inference failed: %s. Continuing without shapes.", e)
```

---

### QUAL-07: `_pool_flops` hardcodes kernel size `[2, 2]`

**File:** `src/analysis/flops.py`, lines 103–105

**Problem:**
```python
def _pool_flops(input_shape: list, output_shape: list) -> int:
    kernel = [2, 2]  # Typical kernel size
    return _product(output_shape) * kernel[0] * kernel[1]
```

This ignores the actual `kernel_shape` attribute on the node. The function signature doesn't accept the node, so it can't access attributes.

**Fix:** Change signature to accept the node (like `_conv_flops`):

```python
def _pool_flops(node: LayerNode, input_shape: list, output_shape: list) -> int:
    kernel = node.attributes.get("kernel_shape", [2, 2])
    k_h = kernel[0] if len(kernel) > 0 else 2
    k_w = kernel[1] if len(kernel) > 1 else 2
    return _product(output_shape) * k_h * k_w
```

And update the call site in `_calculate_layer_flops`.

---

## 🔵 Test Issues

### TEST-01: `test_matmul_flops` passes by coincidence (batch=1)

**File:** `tests/test_analysis/test_flops.py`, lines 26–34

**Problem:**  
The test uses `input_shapes=[[1, 512]]` where `M=1`, hiding the double-counting bug (BUG-02). The assertion `flops == 2 * 1 * 512 * 256` passes because `batch*m = 1*1 = 1`.

**Fix:** Add a test with non-trivial dimensions:

```python
def test_matmul_flops_2d_nontrivial(self):
    """MatMul with 2D input [32, 512] should not double-count."""
    node = _make_node(
        0, "MatMul",
        input_shapes=[[32, 512]],
        output_shapes=[[32, 256]],
    )
    flops = _calculate_layer_flops(node)
    assert flops == 2 * 32 * 512 * 256
```

---

### TEST-02: No tests for `LayerRules._check_activation_after_final_layer`

**File:** `tests/test_analysis/test_rules.py`

**Problem:**  
The `LAYER_004` rule ("No Activation After Final Layer") has zero test coverage.

**Fix:** Add:

```python
def test_no_activation_after_final_layer(self):
    """Final linear layer without activation should trigger INFO."""
    nodes = [
        _make_node(0, "Conv", "convolution"),
        _make_node(1, "MatMul", "linear"),
    ]
    graph = _make_graph(nodes)
    findings = self.rules.check(graph)
    assert any(f.rule_id == "LAYER_004" for f in findings)
```

---

### TEST-03: No tests for `estimate_memory` and `estimate_training_time`

**File:** `tests/test_analysis/` (missing file)

**Problem:**  
The `memory.py` module has zero test coverage. The `estimate_memory` and `estimate_training_time` functions are complex and contain calculations that should be validated.

**Fix:** Create `tests/test_analysis/test_memory.py`:

```python
"""Tests for Memory Estimator."""
import pytest
from src.graph import LayerNode, NeuroScopeGraph
from src.analysis.memory import estimate_memory, estimate_training_time

def test_estimate_memory_basic():
    nodes = [
        LayerNode(id=0, name="a", op_type="Conv", category="conv", params=1000,
                  output_shapes=[[1, 64, 112, 112]]),
    ]
    graph = NeuroScopeGraph(nodes=nodes)
    result = estimate_memory(graph, precision="float32", batch_size=1)
    assert result["weights_bytes"] == 1000 * 4
    assert result["gradients_bytes"] == result["weights_bytes"]
    assert result["total_bytes"] > 0
```

---

### TEST-04: No tests for API routes

**File:** `tests/` (missing directory)

**Problem:**  
None of the FastAPI routes have integration tests. The upload→analyze pipeline is completely untested end-to-end.

**Recommendation:** Add `tests/test_api/test_routes.py` using `fastapi.testclient.TestClient`:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}

def test_upload_unsupported_format():
    resp = client.post("/api/upload", files={"file": ("test.txt", b"data", "text/plain")})
    assert resp.status_code == 400
```

---

## Architecture Notes

### No circular imports detected ✅
The dependency graph is clean: `graph` → `parsers` → `analysis` → `api/routes`.

### Module separation is good ✅
Analysis rules are properly split by scope (layer, architecture, efficiency). Parsers use a base class interface.

### Missing shared state module ⚠️
The `graph_store` pattern in `analyze.py` should be extracted to a shared state module for use by upload, analyze, export, and compare routes.

### CORS is wide open ⚠️
`allow_origins=["*"]` is acceptable for development but must be restricted before production deployment.

---

## Priority Fix Order

1. **BUG-01** — Upload/analyze graph_store disconnect (blocks core workflow)
2. **BUG-02** — `_matmul_flops` double-counting (incorrect FLOPs for all non-batched models)
3. **BUG-04** — Missing `BaseParser` import (test suite crash)
4. **BUG-03** — Stride detection broken (EFF_003 rule never fires)
5. **FUNC-01** — ONNX parser missing `connections_in`/`connections_out` (frontend data incomplete)
6. **FUNC-02** — Double temp file deletion (potential runtime error)
7. **TEST-01** — Add non-trivial matmul test
8. **QUAL-01** through **QUAL-07** — Code clarity improvements
9. **TEST-02** through **TEST-04** — Expand test coverage
10. **FUNC-03**, **FUNC-04** — Implement or properly stub compare/export
