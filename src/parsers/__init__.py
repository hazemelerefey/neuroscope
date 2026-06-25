"""
Base parser interface.

All format-specific parsers (ONNX, PyTorch, Keras, TFLite) implement this interface
and produce a unified NeuroScopeGraph.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.graph import NeuroScopeGraph


class BaseParser(ABC):
    """Abstract base class for model parsers."""

    @abstractmethod
    def parse(self, file_path: str, **kwargs) -> NeuroScopeGraph:
        """
        Parse a model file and produce a NeuroScopeGraph.

        Args:
            file_path: Path to the model file.
            **kwargs: Format-specific options.

        Returns:
            NeuroScopeGraph representation of the model.

        Raises:
            ValueError: If the file format is invalid.
            FileNotFoundError: If the file doesn't exist.
        """
        pass

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """
        Check if this parser supports the given file.

        Args:
            file_path: Path to the model file.

        Returns:
            True if this parser can handle the file.
        """
        pass

    @staticmethod
    def detect_format(file_path: str) -> Optional[str]:
        """
        Detect model format from file extension.

        Args:
            file_path: Path to the model file.

        Returns:
            Format string ("onnx", "pytorch", "keras", "tflite") or None.
        """
        import os

        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            ".onnx": "onnx",
            ".pt": "pytorch",
            ".pth": "pytorch",
            ".h5": "keras",
            ".keras": "keras",
            ".tflite": "tflite",
            ".pb": "tensorflow",
            ".pbtxt": "tensorflow",
        }
        return format_map.get(ext)


def get_all_parsers() -> list[BaseParser]:
    """
    Get instances of all available parsers.

    Returns:
        List of BaseParser instances for all supported formats.
    """
    from src.parsers.onnx_parser import ONNXParser

    parsers: list[BaseParser] = [ONNXParser()]

    # Import optional parsers (gracefully skip if dependencies missing)
    try:
        from src.parsers.pytorch_parser import PyTorchParser
        parsers.append(PyTorchParser())
    except ImportError:
        pass

    try:
        from src.parsers.keras_parser import KerasParser
        parsers.append(KerasParser())
    except ImportError:
        pass

    try:
        from src.parsers.tflite_parser import TFLiteParser
        parsers.append(TFLiteParser())
    except ImportError:
        pass

    return parsers
