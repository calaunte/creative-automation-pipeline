"""
Configuration module for the Creative Automation Pipeline.
Loads settings from environment variables and provides defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    ASSET_STORAGE_PATH = Path(os.getenv('ASSET_STORAGE_PATH', BASE_DIR / 'assets'))
    OUTPUT_PATH = Path(os.getenv('OUTPUT_PATH', BASE_DIR / 'output'))

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'dall-e-3')
    IMAGE_SIZE = os.getenv('IMAGE_SIZE', '1024x1024')
    IMAGE_QUALITY = os.getenv('IMAGE_QUALITY', 'standard')

    # Brand Compliance
    BRAND_LOGO_PATH = Path(os.getenv('BRAND_LOGO_PATH', ASSET_STORAGE_PATH / 'brand' / 'logo.png'))
    BRAND_COLORS = os.getenv('BRAND_COLORS', '#FF0000,#FFFFFF,#000000').split(',')

    # Legal Compliance
    PROHIBITED_WORDS = os.getenv('PROHIBITED_WORDS', 'guarantee,cure,miracle,free').split(',')

    # Aspect Ratios
    ASPECT_RATIOS_STR = os.getenv('ASPECT_RATIOS', '1:1,9:16,16:9')
    ASPECT_RATIOS = [
        tuple(map(int, ratio.split(':')))
        for ratio in ASPECT_RATIOS_STR.split(',')
    ]

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.ASSET_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        (cls.ASSET_STORAGE_PATH / 'brand').mkdir(parents=True, exist_ok=True)
        (cls.ASSET_STORAGE_PATH / 'products').mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set. Please set it in .env file.")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))

        return True


# Ensure directories exist on import
Config.ensure_directories()
