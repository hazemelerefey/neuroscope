"""
Tests for ONNX Parser.
"""

import pytest
import os
import tempfile

# Skip if onnx not installed
onnx = pytest.importorskip("onnx")

from src.parsers.onnx_parser import ONNXParser
from src.graph import NeuroScopeGraph


class TestONNXParser:
    """Test suite for ONNX parser."""

    def setup_method(self):
        self.parser = ONNXParser()

    def test_supports_onnx_files(self):
        assert self.parser.supports("model.onnx") is True
        assert self.parser.supports("model.pt") is False
        assert self.parser.supports("model.h5") is False

    def test_detect_format(self):
        assert BaseParser.detect_format("model.onnx") == "onnx"
        assert BaseParser.detect_format("model.pt") == "pytorch"
        assert BaseParser.detect_format("model.h5") == "keras"
        assert BaseParser.detect_format("model.tflite") == "tflite"
        assert BaseParser.detect_format("model.txt") is None

    def test_parse_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            self.parser.parse("/nonexistent/model.onnx")

    # TODO: Add tests with actual ONNX model files
    # def test_parse_simple_model(self):
    #     graph = self.parser.parse("data/samples/simple_cnn.onnx")
    #     assert isinstance(graph, NeuroScopeGraph)
    #     assert len(graph.nodes) > 0
    #     assert graph.framework == "onnx"
