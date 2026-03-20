# Assets Directory

This directory contains static assets for the MIA system.

## Required Files

### logo.png
**Status**: ⚠️ **USER MUST PROVIDE**

Place your organization's logo here. This logo will be used as:
- Watermark in PDF reports (with configurable opacity)
- Branding element in the report header

**Requirements**:
- Format: PNG (with transparency recommended)
- Recommended size: 500x500 pixels or larger
- Aspect ratio: Square or close to square works best
- File name: Exactly `logo.png`

**Usage**:
The logo is configured in `config.py` under `PDF_CONFIG["logo"]`:
- Display size in PDF: 100x100 points
- Watermark size: 200x200 points
- Opacity: 0.1 (10% for watermark)

## Optional Assets

You can add other assets here as needed:
- Additional images
- Icons
- Templates
- Fonts (if using custom fonts)

All assets in this directory will be ignored by git except for this README.
