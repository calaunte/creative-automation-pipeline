"""
Image Generator Module
Uses GenAI APIs (OpenAI DALL-E) to generate product images.
"""

import logging
import requests
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images using GenAI APIs."""

    def __init__(self, api_key: str, model: str = 'dall-e-3', size: str = '1024x1024', quality: str = 'standard'):
        """
        Initialize image generator.

        Args:
            api_key: OpenAI API key
            model: Model to use (dall-e-3 or dall-e-2)
            size: Image size (1024x1024, 1024x1792, or 1792x1024 for dall-e-3)
            quality: Image quality (standard or hd)
        """
        if not api_key:
            raise ValueError("OpenAI API key is required for image generation")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.size = size
        self.quality = quality

    def generate_product_image(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        campaign_message: str,
        region: str = None,
        style_guidelines: Dict[str, str] = None
    ) -> Optional[bytes]:
        """
        Generate a product image using DALL-E.

        Args:
            product_name: Name of the product
            product_description: Description of the product
            target_audience: Target audience for the campaign
            campaign_message: Core campaign message
            region: Target region for localization
            style_guidelines: Optional style guidelines for image generation

        Returns:
            Image data as bytes, or None if generation fails
        """
        # Build the prompt
        prompt = self._build_prompt(
            product_name,
            product_description,
            target_audience,
            campaign_message,
            region,
            style_guidelines
        )

        logger.info(f"Generating image for '{product_name}' with prompt: {prompt[:100]}...")

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                n=1
            )

            # Get the image URL
            image_url = response.data[0].url

            # Download the image
            image_data = self._download_image(image_url)

            logger.info(f"Successfully generated image for '{product_name}'")
            return image_data

        except Exception as e:
            logger.error(f"Failed to generate image for '{product_name}': {e}")
            return None

    def _build_prompt(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        campaign_message: str,
        region: str = None,
        style_guidelines: Dict[str, str] = None
    ) -> str:
        """
        Build a detailed prompt for image generation.

        Args:
            product_name: Name of the product
            product_description: Description of the product
            target_audience: Target audience
            campaign_message: Campaign message
            region: Target region
            style_guidelines: Style guidelines

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        # Base product description
        if product_description:
            prompt_parts.append(f"A professional marketing photo of {product_name}: {product_description}.")
        else:
            prompt_parts.append(f"A professional marketing photo of {product_name}.")

        # Target audience context
        if target_audience:
            prompt_parts.append(f"Designed to appeal to {target_audience}.")

        # Campaign message context
        if campaign_message:
            prompt_parts.append(f"The image should convey: {campaign_message}.")

        # Regional/cultural adaptation
        if region:
            prompt_parts.append(f"Culturally appropriate for the {region} market.")

        # Style guidelines
        if style_guidelines:
            if 'primary_color' in style_guidelines:
                prompt_parts.append(f"Use {style_guidelines['primary_color']} as a dominant color theme.")
            if 'style' in style_guidelines:
                prompt_parts.append(f"Style: {style_guidelines['style']}.")

        # General quality directives
        prompt_parts.append("High-quality, professional photography, clean composition, commercial advertising style.")

        prompt = " ".join(prompt_parts)

        # Ensure prompt is within reasonable length (DALL-E has a 4000 char limit)
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."

        return prompt

    def _download_image(self, url: str) -> bytes:
        """
        Download image from URL.

        Args:
            url: Image URL

        Returns:
            Image data as bytes
        """
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content

    def test_connection(self) -> bool:
        """
        Test if the API connection is working.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try a simple API call
            self.client.models.list()
            logger.info("OpenAI API connection successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI API connection failed: {e}")
            return False


class MockImageGenerator(ImageGenerator):
    """Mock image generator for testing without API calls."""

    def __init__(self):
        """Initialize mock generator (no API key needed)."""
        self.model = 'mock'
        self.size = '1024x1024'
        self.quality = 'standard'
        # Don't call parent __init__ to avoid requiring API key

    def generate_product_image(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        campaign_message: str,
        region: str = None,
        style_guidelines: Dict[str, str] = None
    ) -> Optional[bytes]:
        """
        Generate a mock/placeholder image.

        Returns:
            Simple placeholder image data
        """
        logger.info(f"Mock: Generating placeholder for '{product_name}'")

        # Try to create a nice placeholder image with PIL
        try:
            from PIL import Image, ImageDraw
            import io

            # Create a 1024x1024 image with a solid color
            img = Image.new('RGB', (1024, 1024), color='#E8E8E8')
            draw = ImageDraw.Draw(img)

            # Add text
            text = f"{product_name}\n[Mock Generated Image]"

            # Try to calculate text position (center)
            try:
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((1024 - text_width) // 2, (1024 - text_height) // 2)
            except:
                # Fallback position if textbbox fails
                position = (350, 500)

            draw.text(position, text, fill='#333333')

            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            logger.info(f"Mock: Generated placeholder image for '{product_name}'")
            return buffer.getvalue()

        except Exception as e:
            logger.warning(f"PIL image creation failed: {e}, creating minimal PNG")
            # Create a minimal valid 1x1 PNG as fallback
            # This is a minimal valid PNG file (1x1 pixel, gray)
            minimal_png = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xa8\xa9\xa9'
                b'\x01\x00\x02\xec\x01u\x90\x1f\x80[\x00\x00\x00\x00IEND\xaeB`\x82'
            )
            logger.info(f"Mock: Generated minimal PNG for '{product_name}'")
            return minimal_png

    def test_connection(self) -> bool:
        """Mock test always returns True."""
        logger.info("Mock: API connection test passed")
        return True
