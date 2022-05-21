# USD-preview-replacer
Parses Nvidia Omniverse USDA file and replaces preview images with full images.

## Why?
Not all connectors have full support for MDL shaders yet, while the Omniverse Preview Surface has a lower quality and sometimes even different scaling than the original textures. The purpose of this script is to replace the preview textures with the original ones without using any MDL shaders.

## Requirements
__Python 3.8 and higher__ (it might run on an earlier version, but it wasn't tested)

__`usd-core`__ library

Omniverse scene saved into __usda__ file with exported preview surface.

## Installation
1. Install Python from [python.org](https://www.python.org/)
2. Open CMD console
    - ### MAC
        To open the console on the Mac desktop app, click "Help" in the Mac menu bar, then select "Developer Tools". This will open the developer console in a new window.

    - ### Windows
        Press Win + R, type `cmd` and hit Enter

3. Run to install dependency
    ```
    pip install usd-core
    ```

## Use
1. Navigate your console into the place where your __usda__ file is located using `cd` command. Example: `cd C:\Users\any-user\Documents\Workspace\Omniverse-scene\`.
2. Place `usd-preview-replacer.py` into the same folder

3. Make a backup of your usda file, just in case

4. Start the script
    ```
    python usd-preview-replacer.py
    ```


It has been tested on a file from Unreal Engine 5. Other sources may require adjustments to the script, so please let me know via the Issues tab if you encounter any issues.