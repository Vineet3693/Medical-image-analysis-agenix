# Sample MRI Images

This directory should contain sample MRI images for testing the MIA workflow.

## Required Format

- **File Format**: JPEG, PNG, or DICOM
- **Recommended Size**: 512x512 pixels or larger
- **Color**: Grayscale or RGB

## Sample Images

Place your test MRI images here. For example:
- `sample_brain_axial.jpg`
- `sample_spine_sagittal.jpg`
- `sample_knee_coronal.jpg`

## Usage

Update the `mri_image_path` in your workflow to point to these images:

```python
initial_state = {
    "mri_image_path": "data/sample_mri/sample_brain_axial.jpg",
    # ...
}
```

## Privacy Note

⚠️ **IMPORTANT**: Do not commit real patient MRI images to version control. Use only de-identified or synthetic test images.
