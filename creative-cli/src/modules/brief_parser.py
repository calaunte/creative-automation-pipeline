"""
Campaign Brief Parser Module
Handles parsing and validation of campaign briefs in JSON or YAML format.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import validate, ValidationError


class CampaignBrief:
    """Represents a validated campaign brief."""

    SCHEMA = {
        "type": "object",
        "required": ["campaign_name", "products", "target_region", "target_audience", "campaign_message"],
        "properties": {
            "campaign_name": {"type": "string", "minLength": 1},
            "products": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["product_id", "product_name"],
                    "properties": {
                        "product_id": {"type": "string"},
                        "product_name": {"type": "string"},
                        "product_description": {"type": ["string", "null"]},
                        "product_image": {"type": ["string", "null"]}
                    }
                }
            },
            "target_region": {"type": "string", "minLength": 1},
            "target_audience": {"type": "string", "minLength": 1},
            "campaign_message": {"type": "string", "minLength": 1},
            "brand_guidelines": {
                "type": "object",
                "properties": {
                    "primary_color": {"type": "string"},
                    "secondary_color": {"type": "string"},
                    "font_family": {"type": "string"}
                }
            },
            "localization": {
                "type": "object",
                "properties": {
                    "languages": {"type": "array", "items": {"type": "string"}},
                    "translations": {"type": "object"}
                }
            },
            "aspect_ratios": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }

    def __init__(self, data: Dict[str, Any]):
        """Initialize campaign brief with validated data."""
        self.validate_schema(data)
        self.data = data

        # Extract key fields
        self.campaign_name = data['campaign_name']
        self.products = data['products']
        self.target_region = data['target_region']
        self.target_audience = data['target_audience']
        self.campaign_message = data['campaign_message']
        self.brand_guidelines = data.get('brand_guidelines', {})
        self.localization = data.get('localization', {})
        self.aspect_ratios = data.get('aspect_ratios', ['1:1', '9:16', '16:9'])

    @classmethod
    def validate_schema(cls, data: Dict[str, Any]) -> bool:
        """Validate data against the campaign brief schema."""
        try:
            validate(instance=data, schema=cls.SCHEMA)
            return True
        except ValidationError as e:
            raise ValueError(f"Campaign brief validation failed: {e.message}")

    @classmethod
    def from_file(cls, file_path: str) -> 'CampaignBrief':
        """Load and parse campaign brief from JSON or YAML file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Campaign brief file not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.json']:
                data = json.load(f)
            elif path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .yaml")

        return cls(data)

    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Get product details by product ID."""
        for product in self.products:
            if product['product_id'] == product_id:
                return product
        raise ValueError(f"Product not found: {product_id}")

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products in the campaign."""
        return self.products

    def get_localized_message(self, language: str = 'en') -> str:
        """Get campaign message in specified language."""
        translations = self.localization.get('translations', {})
        return translations.get(language, self.campaign_message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign brief to dictionary."""
        return self.data

    def __repr__(self) -> str:
        """String representation of campaign brief."""
        return (f"CampaignBrief(name='{self.campaign_name}', "
                f"products={len(self.products)}, "
                f"region='{self.target_region}')")


class BriefParser:
    """Parser for campaign briefs."""

    @staticmethod
    def parse(file_path: str) -> CampaignBrief:
        """Parse campaign brief from file."""
        return CampaignBrief.from_file(file_path)

    @staticmethod
    def validate(file_path: str) -> bool:
        """Validate campaign brief file without creating object."""
        try:
            CampaignBrief.from_file(file_path)
            return True
        except (ValueError, FileNotFoundError) as e:
            print(f"Validation failed: {e}")
            return False
