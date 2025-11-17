"""
ComfyUI-UGC-Video-Generator
Custom nodes for creating AI-generated UGC video variations in ComfyUI
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# ComfyUI will use these to register the nodes
WEB_DIRECTORY = "./web"
__version__ = "1.0.0"
