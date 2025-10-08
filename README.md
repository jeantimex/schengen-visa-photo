# Schengen Visa Photo Processor

An automated Python tool that processes photos to meet Schengen visa requirements. The tool automatically detects faces, removes backgrounds, and crops photos to the exact 35mm × 45mm dimensions required for Schengen visa applications.

## Features

- ✅ **Automatic face detection** and smart cropping
- ✅ **Background removal** using AI (rembg)
- ✅ **Precise sizing** to 35mm × 45mm (413 × 531 pixels at 300 DPI)
- ✅ **Print-ready 4×6 output** with 2 rows × 3 columns layout
- ✅ **Cutting guides** with light grey borders for easy trimming
- ✅ **Image enhancement** (brightness, contrast, sharpness)
- ✅ **Professional white background**

## Requirements

- Python 3.7+
- Virtual environment (recommended)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd schengen-visa-photo
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Process a photo with default settings (background removal + 4×6 print):

```bash
python visa_photo_processor.py input_photo.jpg
```

This will create:
- `output/input_photo_visa.jpg` - Individual visa photo (35mm × 45mm)
- `output/input_photo_visa_4x6_print.jpg` - Print-ready 4×6 sheet with 6 photos

### Advanced Options

```bash
# Specify custom output location
python visa_photo_processor.py input.jpg -o custom/my_visa.jpg

# Skip background removal (keep original background)
python visa_photo_processor.py input.jpg --no-bg-removal

# Create only individual photo (skip 4×6 print version)
python visa_photo_processor.py input.jpg --no-print

# Combine options
python visa_photo_processor.py input.jpg --no-bg-removal --no-print -o my_photo.jpg
```

### Help

```bash
python visa_photo_processor.py --help
```

## Output Examples

### Individual Visa Photo
- **Size:** 35mm × 45mm (413 × 531 pixels)
- **Resolution:** 300 DPI
- **Background:** Clean white
- **Format:** High-quality JPEG

### 4×6 Print Layout
- **Size:** 6" × 4" (1800 × 1200 pixels)
- **Layout:** 2 rows × 3 columns = 6 photos
- **Features:** Light grey cutting guides with margins
- **Perfect for:** Printing at Walgreens, CVS, or any photo lab

## Schengen Visa Photo Requirements

This tool ensures compliance with official Schengen visa photo requirements:

- ✅ Size: 35mm width × 45mm height
- ✅ Head size: 28-34mm (70-80% of photo height)
- ✅ Face position: Centered, looking straight at camera
- ✅ Background: Plain white or light grey
- ✅ Resolution: 300 DPI minimum
- ✅ Format: Color, high quality

## Tips for Best Results

### Input Photo Guidelines
- **High resolution:** Use photos with at least 1200×1500 pixels
- **Good lighting:** Ensure face is well-lit and clearly visible
- **Front-facing:** Person should look directly at the camera
- **Clear background:** Simple backgrounds work best for removal
- **Head position:** Face should be roughly centered in the original photo

### Printing Instructions
1. Use the generated `*_4x6_print.jpg` file
2. Print at any photo lab (Walgreens, CVS, Costco, etc.)
3. Select "4×6 photo print" option
4. Ensure "fit to print" or "no cropping" is selected
5. Cut along the light grey guide lines

## File Structure

```
schengen-visa-photo/
├── visa_photo_processor.py    # Main processing script
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
└── output/                  # Generated photos (auto-created)
    ├── filename_visa.jpg           # Individual visa photo
    └── filename_visa_4x6_print.jpg # Print-ready layout
```

## Dependencies

- **opencv-python** - Face detection and image processing
- **pillow** - Image manipulation and enhancement
- **numpy** - Numerical operations
- **rembg** - AI-powered background removal
- **onnxruntime** - Required by rembg for AI models

## Troubleshooting

### Face Not Detected
- Ensure the face is clearly visible and well-lit
- Try a photo where the person is looking directly at the camera
- The tool will use center crop if face detection fails

### Background Removal Issues
- Use `--no-bg-removal` flag to skip background removal
- Ensure good contrast between subject and background
- Consider using photos with simpler backgrounds

### Print Quality
- Always use the `*_4x6_print.jpg` file for printing
- Ensure your printer/photo lab maintains 300 DPI
- Verify "no cropping" or "fit to print" option is selected

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool helps format photos to meet Schengen visa requirements, but users should verify that their final photos comply with the specific requirements of their target country's embassy or consulate. Photo requirements may vary slightly between different Schengen countries.