# Exporter-X for Fusion 360

A powerful, streamlined Fusion 360 add-in designed for fast, reliable batch exporting of 3D designs and 2D drawings. 

## Features

This add-in provides 4 core commands directly in your Fusion 360 Utilities toolbar:
1. **3D Export (CSV)**: Export specific 3D designs by providing a CSV list of filenames.
2. **2D Export (CSV)**: Export specific 2D drawings by providing a CSV list of filenames.
3. **3D Export (Entire Folder)**: Instantly export every single 3D design located inside a specific folder. 
4. **2D Export (Entire Folder)**: Instantly export every single 2D drawing located inside a specific folder.

## Installation

1. **Download** or clone this repository.
2. **Open Fusion 360**.
3. Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins** (or press `Shift+S`).
4. Click the **green "+"** button next to "My Add-Ins".
5. Navigate to and select the `Exporter-X` folder.
6. The add-in will appear in your list. Click **Run** to start using it.

## Detailed Step-by-Step Usage

1. **Turn on the Add-in**: Go to the Add-Ins menu (or press `Shift+S`), select `Exporter-X`, and ensure it is running. The buttons will appear in your toolbar.
2. **Open a Context File (Required)**: You *must* open a CAD file in Fusion 360 before clicking an export button. The add-in uses your currently open file to trace the active project path and auto-select your folders!
   * *Pro-Tip for Speed*: Open a file that is in the folder nearest to all your export targets. If you have nested folders, try to open a file in a folder that is farthest from the root but still contains all the files you need. Alternatively, put all your target files into a single folder. This makes scanning much faster!
3. **Run the Command**: Click the export button you want to use from the toolbar.
4. **Wait and Verify**: Wait a few seconds to a few minutes (depending on how deeply nested your files are and your internet connection speed). The tool will automatically select the folders based on your open file. You can easily click the dropdowns to change the target folders if you need to search somewhere else.
5. **Choose Destination**: Proceed with the menu, and a prompt will ask you to select a destination folder on your local computer. The tool will then begin exporting all files there.

> **⚠️ Note on Drawing (2D) Exports**: When batch exporting 2D drawings, Fusion 360 will rapidly open and close files on your screen. It might look intense or dangerous, but do not worry—this is completely safe and normal behavior!

## CSV File Format (For CSV Exports)

When using the CSV export commands, provide a simple text file with one filename per line:

```csv
Part_Number_001
Part_Number_002
Bracket_Assembly
```
- No headers are necessary (but if your first row says "Name" or "Part", it will be safely ignored).
- Do not include the file extension (e.g. use `Bracket_Assembly`, not `Bracket_Assembly.f3d`).

## Disclaimer

This is a personal project. While it works great for bulk exports, please use it at your own risk when working with production-level models or critical company data.

## License
Distributed under the MIT License. Feel free to use, modify, and distribute.
