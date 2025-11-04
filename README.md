# Fusion 360 Batch Exporter

A powerful Fusion 360 add-in for batch exporting designs and drawings from your Fusion 360 projects. Supports multiple export formats and automated file discovery.

## Features

### 🚀 Batch Export Designs (3D Files)
- Export multiple `.f3d` files from a CSV list
- Supported formats: **STEP**, **STL**, **OBJ**
- Smart file discovery using cache or live scan
- Progress tracking in Text Commands window

### 📐 Batch Export Drawings (2D Files)
- Export multiple `.f2d` files from a CSV list
- Supported formats: **PDF**, **DXF**, **DWG**
- Automatic drawing product detection
- Reliable batch processing

### 📋 Additional Tools
- **Build Cache**: Create a searchable cache of all your Fusion 360 files
- **Export by File ID**: Export individual files by their Fusion 360 file ID
- **Fetch File ID**: Get the file ID of your currently active document

## Installation

1. **Download** this repository
2. **Extract** to a folder on your computer
3. **Open Fusion 360**
4. Go to **UTILITIES** → **ADD-INS** → **Scripts and Add-Ins** (or press `Shift+S`)
5. Click the **green "+"** button next to "My Add-Ins"
6. Navigate to and select the `ExportWithRohan` folder
7. The add-in should now appear in the list
8. Click **Run** to start using it

## Usage

### Batch Export Designs

1. **Prepare CSV File**
   - Create a CSV file with one design number per line
   - Example:
     ```
     4000009872
     4000009871
     4000009870
     ```

2. **Run Command**
   - In Fusion 360, go to **UTILITIES** → **ADD-INS** panel
   - Find **Batch Export** command
   - Click to run

3. **Select Options**
   - **CSV File**: Browse to your CSV file
   - **Search Mode**: Choose "Use Cache" (faster) or "Live Scan"
   - **Export Format**: Select STEP, STL, or OBJ

4. **Choose Output**
   - Select destination folder
   - Confirm to start batch export

### Batch Export Drawings

1. **Prepare CSV File** (same as above)

2. **Run Command**
   - Find **Batch Export Drawings** command
   - Click to run

3. **Select Options**
   - **CSV File**: Browse to your CSV file
   - **Search Mode**: Choose "Use Cache" or "Live Scan"
   - **Export Format**: Select PDF, DXF, or DWG

4. **Export**
   - Choose output folder
   - Confirm to start

### Build Cache (Recommended First Step)

Building a cache speeds up file discovery dramatically.

1. Run **Build Cache** command
2. Select which projects to cache
3. Wait for completion
4. Cache is saved and reused for future exports

### Export by File ID

For exporting a single file:

1. Run **Export Design** command
2. Choose export format
3. *Optional*: Enter a file ID, or leave blank to export active document
4. Select output folder

### Fetch File ID

To get the Fusion 360 file ID of your current document:

1. Open any design or drawing in Fusion 360
2. Run **Fetch File ID** command
3. File ID is copied to clipboard and shown in message

## CSV File Format

Simple text file with one file number per line:

```
4000009872
4000009871
4000009870
```

- No headers needed
- One design/drawing number per line
- Numbers only (the file ID from Fusion 360)

## How to Find File IDs

**Method 1: Using "Fetch File ID" command**
1. Open the file in Fusion 360
2. Run "Fetch File ID" command
3. ID is copied to clipboard

**Method 2: From Fusion 360 URL**
- When viewing a file in browser, the ID is in the URL:
  `https://myhub.autodesk360.com/...file=urn:adsk.wipprod:fs.file:vf.XXXXXXXXX`
  - The ID is the part after the last `:` 

## Troubleshooting

### "No files found"
- Verify your CSV file has correct file IDs
- Try "Live Scan" instead of "Use Cache"
- Rebuild cache using "Build Cache" command

### Drawing export fails
- Ensure files are actually drawings (`.f2d`), not designs (`.f3d`)
- Check that drawings are accessible in your Fusion 360 account
- Try exporting one file at a time first

### Slow performance
- Use "Build Cache" first, then "Use Cache" mode
- Close other applications to free up memory
- Export in smaller batches

## Technical Details

### File Discovery Methods

**Use Cache (Fast)**
- Reads from pre-built cache file
- Instant lookup
- Recommended for large projects

**Live Scan (Thorough)**
- Scans your entire Fusion 360 data tree
- Slower but always up-to-date
- Use if cache is stale

### Supported Formats

**3D Designs (.f3d)**
- STEP (.stp)
- STL (.stl)
- OBJ (.obj)

**2D Drawings (.f2d)**
- PDF (.pdf)
- DXF (.dxf)
- DWG (.dwg)

## Credits

Developed with insights from:
- [aconz2/Fusion360Exporter](https://github.com/aconz2/Fusion360Exporter) - Drawing export pattern
- Fusion 360 API Community

## License

MIT License - Feel free to use and modify.

## Support

For issues or questions, please open an issue on GitHub.
