from .image_metadata_node import ImageMetadataSaver, ImageMetadataLoader

NODE_CLASS_MAPPINGS = {
    "ImageMetadataSaver": ImageMetadataSaver,
    "ImageMetadataLoader": ImageMetadataLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageMetadataSaver": "Save Image With Metadata (by Light_x02)",
    "ImageMetadataLoader": "Load Image With Metadata (by Light_x02)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
