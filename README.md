# USD-preview-replacer
Parses Nvidia Omniverse USDA file and replaces preview images with full images.

## Why?
Blender does not have full support for MDL shaders yet, while the Omniverse Preview Surface has a lower quality and sometimes even different scaling than the original textures. The purpose of this addon is to replace the preview textures with the original ones whenever possible.

## Requirements
- Blender 3.1 and newer
- Omniverse scene saved into __usda__ file with exported preview surface.

## Installation
1. Download zip archive from the Releases panel on the right
2. Open Blender's addon manager (Edit > Preferences > Addons)
3. Click __Install__ at the top of the window.
4. Select downloaded zip archive


## Use
1. Open your USDA scene in blender, make sure to enable Omniverse Preview Surface on import.
2. Select any object you would like to process
3. Open in the viewport Omniverse tab, scroll to the bottom to find the addon's functionality:
![Alt text](readme_images/screenshot1.png?raw=true "Screenshot 1")
4. Select your USDA file you used during import in the first field
5. Click __Replace Previews__ button.



It has been tested on a file from Unreal Engine 5. Other sources may require adjustments to the script, so please let me know via the Issues tab if you encounter any issues.