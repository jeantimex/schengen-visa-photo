#!/usr/bin/env python3
"""
Schengen Visa Photo Processor

This script processes photos to meet Schengen visa requirements:
- Size: 35mm x 45mm (approximately 413 x 531 pixels at 300 DPI)
- Background removal
- Automatic face detection and cropping
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
import argparse
import os
import sys

class VisaPhotoProcessor:
    def __init__(self):
        # Schengen visa photo dimensions (35mm x 45mm at 300 DPI)
        self.target_width_mm = 35
        self.target_height_mm = 45
        self.dpi = 300

        # Convert mm to pixels at 300 DPI
        self.target_width_px = int((self.target_width_mm / 25.4) * self.dpi)  # 413 pixels
        self.target_height_px = int((self.target_height_mm / 25.4) * self.dpi)  # 531 pixels

        # 4x6 inch print dimensions at 300 DPI (6" wide × 4" tall)
        self.print_width_px = 6 * self.dpi  # 1800 pixels
        self.print_height_px = 4 * self.dpi  # 1200 pixels

        # Load face detection classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_face(self, image):
        """Detect the largest face in the image and return its bounding box."""
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Try multiple detection parameters for better accuracy
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(100, 100)  # Minimum face size
        )

        if len(faces) == 0:
            # Try with more relaxed parameters
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 3)

        if len(faces) == 0:
            print("Warning: No face detected. Using center crop.")
            return None

        # Get the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        print(f"Face detected: {largest_face}")
        return largest_face

    def remove_background(self, image):
        """Remove background using rembg."""
        try:
            # Convert PIL image to bytes
            import io
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()

            # Remove background
            result = remove(img_bytes)

            # Convert back to PIL image
            return Image.open(io.BytesIO(result)).convert("RGBA")
        except Exception as e:
            print(f"Warning: Background removal failed: {e}")
            return image.convert("RGBA")

    def crop_and_resize(self, image, face_box=None):
        """Crop the image around the face and resize to visa photo dimensions."""
        width, height = image.size
        target_aspect_ratio = self.target_width_px / self.target_height_px

        if face_box is not None:
            x, y, w, h = face_box
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # For passport photos, focus more on the face area
            # Use a reasonable head-to-photo ratio
            head_to_photo_ratio = 0.70

            # Face detection usually gets about 60-70% of the actual head height
            estimated_head_height = h * 1.3

            # Calculate photo dimensions based on head size
            photo_height = estimated_head_height / head_to_photo_ratio
            photo_width = photo_height * target_aspect_ratio

            # Center the crop on the FACE itself, not just position face in frame
            # Move the crop center up to focus on face rather than including full head
            face_offset_y = h * 0.3  # Move crop center up by 30% of face height from face center
            crop_center_y = face_center_y - face_offset_y  # Focus on upper part of face
            crop_center_x = face_center_x  # Keep horizontal centering on face

            # Calculate crop position based on the new face-focused center
            crop_y = crop_center_y - (photo_height / 2)
            crop_x = crop_center_x - (photo_width / 2)

            # Ensure crop stays within image boundaries
            crop_x = max(0, min(crop_x, width - photo_width))
            crop_y = max(0, min(crop_y, height - photo_height))

            # If photo dimensions are too large for the image, scale down
            if photo_width > width or photo_height > height:
                scale_factor = min(width / photo_width, height / photo_height) * 0.95
                photo_width *= scale_factor
                photo_height *= scale_factor

                # Recalculate position
                crop_x = face_center_x - (photo_width / 2)
                crop_y = face_center_y - (photo_height * face_position_ratio)
                crop_x = max(0, min(crop_x, width - photo_width))
                crop_y = max(0, min(crop_y, height - photo_height))

            crop_box = (int(crop_x), int(crop_y), int(crop_x + photo_width), int(crop_y + photo_height))
            print(f"Face-based crop: {crop_box}")

        else:
            # No face detected, use center crop with target aspect ratio
            if width / height > target_aspect_ratio:
                # Image is wider, crop width
                new_width = int(height * target_aspect_ratio)
                crop_x = (width - new_width) // 2
                crop_box = (crop_x, 0, crop_x + new_width, height)
            else:
                # Image is taller, crop height
                new_height = int(width / target_aspect_ratio)
                crop_y = (height - new_height) // 4  # Crop more from bottom
                crop_box = (0, crop_y, width, crop_y + new_height)
            print(f"Center crop: {crop_box}")

        # Crop the image
        cropped = image.crop(crop_box)

        # Verify the cropped image has the correct aspect ratio
        crop_width, crop_height = cropped.size
        crop_aspect_ratio = crop_width / crop_height

        print(f"Crop dimensions: {crop_width}x{crop_height}, aspect ratio: {crop_aspect_ratio:.3f}")
        print(f"Target aspect ratio: {target_aspect_ratio:.3f}")

        # Resize to exact visa photo dimensions
        resized = cropped.resize((self.target_width_px, self.target_height_px), Image.LANCZOS)

        return resized

    def add_white_background(self, image):
        """Add a white background to the image."""
        # Create a white background
        background = Image.new("RGB", image.size, (255, 255, 255))

        if image.mode == "RGBA":
            # Composite the image over the white background
            background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
        else:
            background.paste(image)

        return background

    def enhance_image(self, image):
        """Apply basic image enhancements for better photo quality."""
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Slight brightness and contrast enhancement
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)

        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)

        return image

    def create_4x6_print(self, visa_photo):
        """Create a 4x6 inch print (6" wide × 4" tall) with 2 rows × 3 columns of visa photos."""
        from PIL import ImageDraw

        # Create a white 4x6 background (6" wide × 4" tall)
        print_image = Image.new("RGB", (self.print_width_px, self.print_height_px), (255, 255, 255))
        draw = ImageDraw.Draw(print_image)

        # Fixed layout: 2 rows × 3 columns = 6 photos
        photos_per_row = 3  # 3 columns
        photos_per_col = 2  # 2 rows

        # Add margin around each photo for easier cutting
        photo_margin = 10  # pixels margin around each photo

        print(f"4x6 print (6\"×4\") will contain {photos_per_row} columns × {photos_per_col} rows = {photos_per_row * photos_per_col} photos")

        # Calculate cell dimensions including margins
        cell_width = self.target_width_px + (2 * photo_margin)
        cell_height = self.target_height_px + (2 * photo_margin)

        # Calculate spacing to center the grid
        total_grid_width = photos_per_row * cell_width
        total_grid_height = photos_per_col * cell_height

        start_x = (self.print_width_px - total_grid_width) // 2
        start_y = (self.print_height_px - total_grid_height) // 2

        # Place photos in a 2×3 grid with borders
        for row in range(photos_per_col):
            for col in range(photos_per_row):
                # Calculate cell position
                cell_x = start_x + (col * cell_width)
                cell_y = start_y + (row * cell_height)

                # Calculate photo position within cell (centered with margin)
                photo_x = cell_x + photo_margin
                photo_y = cell_y + photo_margin

                # Paste the photo
                print_image.paste(visa_photo, (photo_x, photo_y))

                # Draw light grey border around the photo
                border_color = (230, 230, 230)  # Very light grey
                border_thickness = 1

                # Draw border rectangle around the photo
                draw.rectangle(
                    [photo_x - border_thickness, photo_y - border_thickness,
                     photo_x + self.target_width_px + border_thickness,
                     photo_y + self.target_height_px + border_thickness],
                    outline=border_color,
                    width=border_thickness
                )

        return print_image

    def process_photo(self, input_path, output_path, remove_bg=True, create_print=True):
        """Main processing function."""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")

            # Load the image
            image = Image.open(input_path)
            print(f"Loaded image: {image.size[0]}x{image.size[1]} pixels")

            # Detect face
            face_box = self.detect_face(image)
            if face_box is not None:
                print(f"Face detected at: {face_box}")

            # Remove background if requested
            if remove_bg:
                print("Removing background...")
                image = self.remove_background(image)

            # Crop and resize to visa photo dimensions
            print("Cropping and resizing...")
            image = self.crop_and_resize(image, face_box)

            # Add white background
            print("Adding white background...")
            image = self.add_white_background(image)

            # Enhance image quality
            print("Enhancing image...")
            image = self.enhance_image(image)

            # Save the individual visa photo
            image.save(output_path, "JPEG", quality=95, dpi=(self.dpi, self.dpi))
            print(f"Visa photo saved to: {output_path}")
            print(f"Final dimensions: {self.target_width_px}x{self.target_height_px} pixels ({self.target_width_mm}x{self.target_height_mm}mm at {self.dpi} DPI)")

            # Create 4x6 print version if requested
            if create_print:
                print_image = self.create_4x6_print(image)
                print_output_path = output_path.replace('.jpg', '_4x6_print.jpg')
                print_image.save(print_output_path, "JPEG", quality=95, dpi=(self.dpi, self.dpi))
                print(f"4x6 print version saved to: {print_output_path}")
                print(f"Print dimensions: {self.print_width_px}x{self.print_height_px} pixels (6\"×4\" with 2×3 layout at {self.dpi} DPI)")

            return True

        except Exception as e:
            print(f"Error processing photo: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Process photos for Schengen visa requirements")
    parser.add_argument("input", help="Input photo file path")
    parser.add_argument("-o", "--output", help="Output photo file path (default: input_visa.jpg)")
    parser.add_argument("--no-bg-removal", action="store_true", help="Skip background removal")
    parser.add_argument("--no-print", action="store_true", help="Skip creating 4x6 print version")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)

    # Generate output filename if not provided
    if args.output is None:
        input_filename = os.path.basename(args.input)
        base_name = os.path.splitext(input_filename)[0]
        args.output = f"output/{base_name}_visa.jpg"

    # Process the photo
    processor = VisaPhotoProcessor()
    success = processor.process_photo(
        args.input,
        args.output,
        remove_bg=not args.no_bg_removal,
        create_print=not args.no_print
    )

    if success:
        print("\nPhoto processing completed successfully!")
        print(f"Your Schengen visa photo is ready: {args.output}")
    else:
        print("\nPhoto processing failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()