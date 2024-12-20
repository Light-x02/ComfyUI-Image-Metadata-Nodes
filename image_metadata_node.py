import os
import json
import datetime
from PIL import Image, PngImagePlugin, ImageSequence, ImageOps
import numpy as np
import torch
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict
from comfy.cli_args import args
import folder_paths

# Image Metadata Loader and Saver Nodes
# Developed by Light_x02
# These nodes allow loading and saving images while preserving metadata.

# Node to load image with metadata
class ImageMetadataLoader(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required": {"image": (sorted(files), {"image_upload": True})}}

    CATEGORY = "image"

    RETURN_TYPES = ("IMAGE", "METADATA")
    FUNCTION = "load_image_with_metadata"
    DESCRIPTION = "Loads images with original metadata intact. Developed by Light_x02."

    def load_image_with_metadata(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)

        metadata = img.info.copy()
        output_images = []
        w, h = None, None

        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)
            if frame.mode == 'I':
                frame = frame.point(lambda x: x * (1 / 255))
            frame = frame.convert("RGB")

            if len(output_images) == 0:
                w, h = frame.size

            if frame.size != (w, h):
                continue

            image_tensor = np.array(frame).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_tensor)[None,]
            output_images.append(image_tensor)

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
        else:
            output_image = output_images[0]

        return (output_image, metadata)

# Node to save image with metadata
class ImageMetadataSaver(ComfyNodeABC):
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "metadata": ("METADATA", {"default": {}, "tooltip": "Original metadata to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. Use %date:yyyy-MM-dd% or %time:HH-mm-ss% for dynamic values."}),
                "subdirectory_name": ("STRING", {"default": "", "tooltip": "Optional subdirectory. Use %date:yyyy-MM-dd% for dynamic dates."})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"
    DESCRIPTION = "Saves images with metadata intact. Developed by Light_x02."

    def save_images(self, images, metadata={}, filename_prefix="ComfyUI", subdirectory_name=""):
        # Replace %date:yyyy-MM-dd% and %time:HH-mm-ss% with dynamic values
        if "%date:yyyy-MM-dd%" in filename_prefix:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            filename_prefix = filename_prefix.replace("%date:yyyy-MM-dd%", current_date)
        if "%time:HH-mm-ss%" in filename_prefix:
            current_time = datetime.datetime.now().strftime("%H-%M-%S")
            filename_prefix = filename_prefix.replace("%time:HH-mm-ss%", current_time)

        # Replace %date:yyyy-MM-dd% with the current date in subdirectory_name
        if "%date:yyyy-MM-dd%" in subdirectory_name:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            subdirectory_name = subdirectory_name.replace("%date:yyyy-MM-dd%", current_date)

        filename_prefix += self.prefix_append
        if subdirectory_name:
            full_output_folder = os.path.join(self.output_dir, subdirectory_name)
        else:
            full_output_folder = self.output_dir

        # Ensure the subdirectory exists
        os.makedirs(full_output_folder, exist_ok=True)

        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, full_output_folder, images[0].shape[1], images[0].shape[0]
        )
        results = []
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Use the provided metadata directly
            pnginfo = PngImagePlugin.PngInfo()
            for key, value in metadata.items():
                pnginfo.add_text(key, value if isinstance(value, str) else json.dumps(value))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"

            img.save(os.path.join(full_output_folder, file), pnginfo=pnginfo, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": os.path.join(subfolder, subdirectory_name) if subdirectory_name else subfolder,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}}

# Register both nodes with new names
NODE_CLASS_MAPPINGS = {
    "ImageMetadataLoader": ImageMetadataLoader,
    "ImageMetadataSaver": ImageMetadataSaver
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageMetadataLoader": "Image Metadata Loader (by Light_x02)",
    "ImageMetadataSaver": "Image Metadata Saver (by Light_x02)"
}
