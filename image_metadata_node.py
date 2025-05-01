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
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {"required": {"image": (sorted(files), {"image_upload": True})}}

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True

    CATEGORY = "image"
    RETURN_TYPES = ("IMAGE", "METADATA", "MASK")
    FUNCTION = "load_image_with_metadata"
    DESCRIPTION = "Loads images with original metadata intact. Developed by Light_x02."

    def load_image_with_metadata(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)

        metadata = img.info.copy()
        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)
            if frame.mode == 'I':
                frame = frame.point(lambda x: x * (1 / 255))
            rgb_frame = frame.convert("RGB")

            if len(output_images) == 0:
                w, h = rgb_frame.size

            if rgb_frame.size != (w, h):
                continue

            image_tensor = np.array(rgb_frame).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_tensor)[None,]
            output_images.append(image_tensor)

            if 'A' in frame.getbands():
                mask = np.array(frame.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif frame.mode == 'P' and 'transparency' in frame.info:
                mask = np.array(frame.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, metadata, output_mask)


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
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. Use %date:yyyy-MM-dd% or %time:HH-mm-ss% for dynamic values."}),
                "subdirectory_name": ("STRING", {"default": "", "tooltip": "Optional subdirectory. Use %date:yyyy-MM-dd% for dynamic dates."})
            },
            "optional": {
                "metadata": ("METADATA", {})
            }
        }

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
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. Supports: %date:yyyy-MM-dd%, %date:yyyy-MM%, %date:yyyy%, %date:MM%, %date:dd%, %time:HH-mm-ss%, %time:HH%, %time:mm%, %time:ss%, %datetime:full% (filename only)."}),
                "subdirectory_name": ("STRING", {"default": "", "tooltip": "Optional subdirectory. Avoid using %datetime:full% here to prevent excessive nesting."})
            },
            "optional": {
                "metadata": ("METADATA", {})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"
    DESCRIPTION = "Saves images with metadata intact. Developed by Light_x02."

    def save_images(self, images, metadata={}, filename_prefix="ComfyUI", subdirectory_name=""):
        if metadata is None:
            metadata = {}

        if "%datetime:full%" in subdirectory_name:
            raise ValueError("The placeholder %datetime:full% is not allowed in subdirectory_name to avoid excessive folder nesting.")

        now = datetime.datetime.now()
        replacements = {
            "%date:yyyy-MM-dd%": now.strftime("%Y-%m-%d"),
            "%date:yyyy-MM%": now.strftime("%Y-%m"),
            "%date:yyyy%": now.strftime("%Y"),
            "%date:MM%": now.strftime("%m"),
            "%date:dd%": now.strftime("%d"),
            "%time:HH-mm-ss%": now.strftime("%H-%M-%S"),
            "%time:HH%": now.strftime("%H"),
            "%time:mm%": now.strftime("%M"),
            "%time:ss%": now.strftime("%S"),
            "%datetime:full%": now.strftime("%Y-%m-%d_%H-%M-%S")
        }

        for key, value in replacements.items():
            filename_prefix = filename_prefix.replace(key, value)
            if key != "%datetime:full%":
                subdirectory_name = subdirectory_name.replace(key, value)

        filename_prefix += self.prefix_append
        if subdirectory_name:
            full_output_folder = os.path.join(self.output_dir, subdirectory_name)
        else:
            full_output_folder = self.output_dir

        os.makedirs(full_output_folder, exist_ok=True)

        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, full_output_folder, images[0].shape[1], images[0].shape[0]
        )
        results = []
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

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
