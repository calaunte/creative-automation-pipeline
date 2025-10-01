"""
Creative Generator Module
Handles image resizing, text overlay, and multi-format creative generation.
"""

import logging
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)


class CreativeGenerator:
    """Generates creative assets in multiple formats with text overlays."""

    def __init__(self):
        """Initialize creative generator."""
        self.default_font_size = 60
        self.default_text_color = (255, 255, 255)  # White
        self.default_bg_color = (0, 0, 0, 180)     # Semi-transparent black

    def generate_multi_format(
        self,
        source_image: bytes,
        aspect_ratios: List[Tuple[int, int]],
        campaign_message: str,
        product_name: str,
        output_base_path: Path,
        brand_color: str = None
    ) -> List[Path]:
        """
        Generate multiple creative formats from a source image.

        Args:
            source_image: Source image as bytes
            aspect_ratios: List of (width, height) aspect ratio tuples
            campaign_message: Text to overlay on the creative
            product_name: Product name for file naming
            output_base_path: Base directory for outputs
            brand_color: Optional brand color for text background

        Returns:
            List of paths to generated creatives
        """
        generated_paths = []

        # Load source image
        img = Image.open(io.BytesIO(source_image))

        # Ensure image is in RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')

        logger.info(f"Generating {len(aspect_ratios)} format variants for {product_name}")

        for aspect_ratio in aspect_ratios:
            try:
                creative_path = self._generate_format(
                    img,
                    aspect_ratio,
                    campaign_message,
                    product_name,
                    output_base_path,
                    brand_color
                )
                generated_paths.append(creative_path)
                logger.info(f"Generated {aspect_ratio[0]}:{aspect_ratio[1]} format: {creative_path.name}")

            except Exception as e:
                logger.error(f"Failed to generate {aspect_ratio} format: {e}")

        return generated_paths

    def _generate_format(
        self,
        img: Image.Image,
        aspect_ratio: Tuple[int, int],
        campaign_message: str,
        product_name: str,
        output_base_path: Path,
        brand_color: str = None
    ) -> Path:
        """
        Generate a single creative format.

        Args:
            img: Source PIL Image
            aspect_ratio: (width, height) aspect ratio tuple
            campaign_message: Campaign message text
            product_name: Product name
            output_base_path: Output directory
            brand_color: Optional brand color

        Returns:
            Path to generated creative
        """
        # Calculate target dimensions maintaining aspect ratio
        target_width, target_height = self._calculate_dimensions(
            img.size,
            aspect_ratio
        )

        # Resize and crop image to target aspect ratio
        creative_img = self._resize_and_crop(img, (target_width, target_height))

        # Add text overlay
        creative_img = self._add_text_overlay(
            creative_img,
            campaign_message,
            brand_color
        )

        # Create output directory if it doesn't exist
        aspect_ratio_dir = output_base_path / f"{aspect_ratio[0]}x{aspect_ratio[1]}"
        aspect_ratio_dir.mkdir(parents=True, exist_ok=True)

        # Save the creative
        output_path = aspect_ratio_dir / f"{product_name}_{aspect_ratio[0]}x{aspect_ratio[1]}.jpg"
        creative_img.save(output_path, 'JPEG', quality=95)

        return output_path

    def _calculate_dimensions(
        self,
        source_size: Tuple[int, int],
        aspect_ratio: Tuple[int, int],
        max_size: int = 1920
    ) -> Tuple[int, int]:
        """
        Calculate target dimensions based on aspect ratio.

        Args:
            source_size: (width, height) of source image
            aspect_ratio: (width, height) aspect ratio
            max_size: Maximum dimension size

        Returns:
            (width, height) target dimensions
        """
        ratio_w, ratio_h = aspect_ratio

        # Calculate dimensions maintaining aspect ratio
        if ratio_w >= ratio_h:
            # Landscape or square
            width = max_size
            height = int(max_size * ratio_h / ratio_w)
        else:
            # Portrait
            height = max_size
            width = int(max_size * ratio_w / ratio_h)

        return (width, height)

    def _resize_and_crop(
        self,
        img: Image.Image,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Resize and crop image to exact target size.

        Args:
            img: Source PIL Image
            target_size: (width, height) target size

        Returns:
            Resized and cropped PIL Image
        """
        target_width, target_height = target_size
        img_width, img_height = img.size

        # Calculate aspect ratios
        img_aspect = img_width / img_height
        target_aspect = target_width / target_height

        if img_aspect > target_aspect:
            # Image is wider than target - crop width
            new_height = img_height
            new_width = int(new_height * target_aspect)
        else:
            # Image is taller than target - crop height
            new_width = img_width
            new_height = int(new_width / target_aspect)

        # Calculate crop box (center crop)
        left = (img_width - new_width) // 2
        top = (img_height - new_height) // 2
        right = left + new_width
        bottom = top + new_height

        # Crop and resize
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize(target_size, Image.Resampling.LANCZOS)

        return img_resized

    def _add_text_overlay(
        self,
        img: Image.Image,
        text: str,
        brand_color: str = None
    ) -> Image.Image:
        """
        Add text overlay to image.

        Args:
            img: PIL Image
            text: Text to overlay
            brand_color: Optional brand color for background

        Returns:
            PIL Image with text overlay
        """
        if not text:
            return img

        # Create a copy to avoid modifying original
        img_with_text = img.copy()
        draw = ImageDraw.Draw(img_with_text, 'RGBA')

        # Image dimensions
        img_width, img_height = img.size

        # Calculate font size based on image size
        font_size = max(30, int(img_height * 0.05))

        # Try to load a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Word wrap text to fit image width
        wrapped_text = self._wrap_text(text, font, img_width - 100, draw)

        # Calculate text bounding box
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position text at bottom center
        padding = 40
        text_x = (img_width - text_width) // 2
        text_y = img_height - text_height - padding * 2

        # Draw semi-transparent background rectangle
        bg_color = self._parse_color(brand_color) if brand_color else self.default_bg_color
        bg_rect = [
            text_x - padding,
            text_y - padding,
            text_x + text_width + padding,
            text_y + text_height + padding
        ]
        draw.rectangle(bg_rect, fill=bg_color)

        # Draw text
        draw.multiline_text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=self.default_text_color,
            align='center'
        )

        return img_with_text

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.ImageDraw
    ) -> str:
        """
        Wrap text to fit within max width.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            Wrapped text with newlines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)

            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width and len(current_line) > 1:
                # Remove last word and add line
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def _parse_color(self, color_str: str) -> Tuple[int, int, int, int]:
        """
        Parse color string to RGBA tuple.

        Args:
            color_str: Color string (hex format like #RRGGBB)

        Returns:
            (R, G, B, A) tuple
        """
        if not color_str:
            return self.default_bg_color

        # Remove # if present
        color_str = color_str.lstrip('#')

        # Parse hex color
        if len(color_str) == 6:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b, 180)  # 180 alpha for semi-transparency

        return self.default_bg_color

    def add_logo_overlay(
        self,
        img: Image.Image,
        logo_path: Path,
        position: str = 'top-right',
        scale: float = 0.15
    ) -> Image.Image:
        """
        Add logo overlay to image.

        Args:
            img: PIL Image
            logo_path: Path to logo image
            position: Position of logo ('top-left', 'top-right', 'bottom-left', 'bottom-right')
            scale: Logo scale relative to image size

        Returns:
            PIL Image with logo overlay
        """
        if not logo_path.exists():
            logger.warning(f"Logo not found: {logo_path}")
            return img

        # Load logo
        logo = Image.open(logo_path)

        # Ensure logo has alpha channel
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')

        # Calculate logo size
        img_width, img_height = img.size
        logo_width = int(img_width * scale)
        logo_aspect = logo.size[1] / logo.size[0]
        logo_height = int(logo_width * logo_aspect)

        # Resize logo
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Calculate position
        padding = 20
        if position == 'top-left':
            pos = (padding, padding)
        elif position == 'top-right':
            pos = (img_width - logo_width - padding, padding)
        elif position == 'bottom-left':
            pos = (padding, img_height - logo_height - padding)
        else:  # bottom-right
            pos = (img_width - logo_width - padding, img_height - logo_height - padding)

        # Create a copy and paste logo
        img_with_logo = img.copy()
        if img_with_logo.mode != 'RGBA':
            img_with_logo = img_with_logo.convert('RGBA')

        img_with_logo.paste(logo, pos, logo)

        # Convert back to RGB
        if img_with_logo.mode == 'RGBA':
            background = Image.new('RGB', img_with_logo.size, (255, 255, 255))
            background.paste(img_with_logo, mask=img_with_logo.split()[3])
            img_with_logo = background

        return img_with_logo
