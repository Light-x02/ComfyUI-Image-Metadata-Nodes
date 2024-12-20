# ComfyUI Image Metadata Nodes

**Version**: 1.0.0  
**Author**: [Light-x02](https://github.com/Light-x02)

## Support My Work
If you find this project useful, you can support my work on Ko-fi:  
[https://ko-fi.com/light_x02](https://ko-fi.com/light_x02)

## Description
This project provides two complementary nodes for **ComfyUI**, allowing you to load and save images while preserving their metadata intact. These nodes are particularly useful for workflows that require image adjustments, such as **upscaling**, without altering the original metadata.

## How It Works

### Metadata Loading
The **Image Metadata Loader** node imports an image while extracting its original metadata, which can then be passed to other nodes.

### Metadata Saving
The **Image Metadata Saver** node saves an image with its original, unchanged metadata embedded directly in the generated PNG file.

By connecting these two nodes through the `METADATA` output/input, you can import a previously generated image with correct metadata, modify it (e.g., using upscaling), and save it while preserving the metadata intact.

## Features
- **Supported Formats**: Load and save in PNG format (metadata is directly embedded in the file).  
- **Dynamic Metadata Management**: Preserves original metadata, even in complex workflows.  
- **Advanced Compatibility**: Metadata is correctly embedded in the final PNG file.

## Installation
1. **Download or Clone the Project**  
   Clone the repository from GitHub:  
   [https://github.com/Light-x02/ComfyUI-Image-Metadata-Nodes](https://github.com/Light-x02/ComfyUI-Image-Metadata-Nodes)

2. **Move the Folder to Your ComfyUI Directory**  
   Copy the folder `ComfyUI_Image_Metadata` into the `custom_nodes` directory of your ComfyUI installation.


3. **Restart ComfyUI**  
Once the files are in place, restart ComfyUI to load the nodes.

## Usage

### Included Nodes

#### Image Metadata Loader
- **Description**: Loads an image and extracts its metadata.  
- **Outputs**:  
- `IMAGE`: The loaded image.  
- `METADATA`: The raw metadata.

#### Image Metadata Saver
- **Description**: Saves an image with unchanged metadata.  
- **Inputs**:  
- `IMAGE`: The image to save.  
- `METADATA`: The metadata to include.  
- **Options**:  
- **Filename Prefix**: Prefix for the file name (e.g., `%date:yyyy-MM-dd%`).  
- **Subdirectory Name**: Name of the subdirectory for saving files.

### Example Workflow
1. Use the **Image Metadata Loader** node to load an image and retrieve its metadata.  
2. Modify the image (e.g., with an upscaling or retouching node).  
3. Connect the `METADATA` output of the loader to the `METADATA` input of the saver.  
4. Use **Image Metadata Saver** to save the image with intact metadata.
   
![Workflow Example](assets/exemple_workflow.png)

## Additional Notes

To save metadata in my PNG files when generating images with txt2img workflows, I use the extension **"ComfyUI-ImageMetadataExtension"**, which is available [here](https://github.com/edelvarden/ComfyUI-ImageMetadataExtension). This ensures that platforms like Civitai automatically detect the metadata.


## License
This project is licensed under the **MIT License**. You are free to use, modify, and distribute it, provided you include a copyright notice.

## Contribution
Contributions are welcome! If you want to report a bug or suggest an improvement, open an issue or submit a pull request on the [GitHub repository](https://github.com/Light-x02/ComfyUI-Image-Metadata-Nodes).

