# Changelog

## [1.0.1] - 2024-12-20
### Fixed
- Fixed an issue where the image size increased after saving, even when no modifications were made to the image.
- Updated `compress_level` in the `ImageMetadataSaver` node to use `self.compress_level`, allowing proper control of output file size.

## [1.0.0] - 2024-12-20
### Added
- Initial release of the **Image Metadata Nodes**.
- Includes:
  - `ImageMetadataLoader` node to load images with metadata.
  - `ImageMetadataSaver` node to save images with metadata intact.