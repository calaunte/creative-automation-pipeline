"""
Asset Manager Module
Handles asset storage, retrieval, and caching for the creative automation pipeline.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import shutil
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages asset storage and retrieval."""

    def __init__(self, storage_path: Path):
        """
        Initialize asset manager.

        Args:
            storage_path: Base path for asset storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.products_path = self.storage_path / 'products'
        self.brand_path = self.storage_path / 'brand'
        self.generated_path = self.storage_path / 'generated'

        for path in [self.products_path, self.brand_path, self.generated_path]:
            path.mkdir(parents=True, exist_ok=True)

    def get_product_asset(self, product_id: str, asset_name: str = None) -> Optional[Path]:
        """
        Get path to product asset if it exists.

        Args:
            product_id: Unique product identifier
            asset_name: Optional specific asset name

        Returns:
            Path to asset if found, None otherwise
        """
        product_dir = self.products_path / product_id

        if not product_dir.exists():
            logger.debug(f"Product directory not found: {product_id}")
            return None

        if asset_name:
            asset_path = product_dir / asset_name
            return asset_path if asset_path.exists() else None

        # Find any image file in the product directory
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        for ext in image_extensions:
            for asset_path in product_dir.glob(f'*{ext}'):
                return asset_path

        logger.debug(f"No assets found for product: {product_id}")
        return None

    def save_product_asset(self, product_id: str, asset_path: str, asset_name: str = None) -> Path:
        """
        Save a product asset to storage.

        Args:
            product_id: Unique product identifier
            asset_path: Source path of the asset
            asset_name: Optional name for the asset (uses original name if not provided)

        Returns:
            Path where asset was saved
        """
        product_dir = self.products_path / product_id
        product_dir.mkdir(parents=True, exist_ok=True)

        source = Path(asset_path)
        if not source.exists():
            raise FileNotFoundError(f"Source asset not found: {asset_path}")

        dest_name = asset_name or source.name
        dest_path = product_dir / dest_name

        shutil.copy2(source, dest_path)
        logger.info(f"Saved product asset: {dest_path}")

        return dest_path

    def get_brand_asset(self, asset_name: str) -> Optional[Path]:
        """
        Get path to brand asset if it exists.

        Args:
            asset_name: Name of the brand asset (e.g., 'logo.png')

        Returns:
            Path to asset if found, None otherwise
        """
        asset_path = self.brand_path / asset_name

        if asset_path.exists():
            return asset_path

        logger.debug(f"Brand asset not found: {asset_name}")
        return None

    def save_generated_asset(
        self,
        asset_data: bytes,
        campaign_name: str,
        product_id: str,
        asset_type: str = 'generated',
        extension: str = 'png'
    ) -> Path:
        """
        Save a generated asset to storage.

        Args:
            asset_data: Binary data of the asset
            campaign_name: Name of the campaign
            product_id: Product identifier
            asset_type: Type of asset (e.g., 'generated', 'hero')
            extension: File extension

        Returns:
            Path where asset was saved
        """
        campaign_dir = self.generated_path / campaign_name / product_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename using content hash
        content_hash = hashlib.md5(asset_data).hexdigest()[:8]
        filename = f"{asset_type}_{content_hash}.{extension}"
        asset_path = campaign_dir / filename

        with open(asset_path, 'wb') as f:
            f.write(asset_data)

        logger.info(f"Saved generated asset: {asset_path}")
        return asset_path

    def asset_exists(self, product_id: str) -> bool:
        """
        Check if any assets exist for a product.

        Args:
            product_id: Product identifier

        Returns:
            True if assets exist, False otherwise
        """
        return self.get_product_asset(product_id) is not None

    def list_product_assets(self, product_id: str) -> list:
        """
        List all assets for a product.

        Args:
            product_id: Product identifier

        Returns:
            List of asset paths
        """
        product_dir = self.products_path / product_id

        if not product_dir.exists():
            return []

        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        assets = []

        for ext in image_extensions:
            assets.extend(list(product_dir.glob(f'*{ext}')))

        return assets

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about asset storage.

        Returns:
            Dictionary with storage statistics
        """
        def get_dir_size(path: Path) -> int:
            """Calculate total size of directory."""
            total = 0
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
            return total

        return {
            'storage_path': str(self.storage_path),
            'total_size_mb': round(get_dir_size(self.storage_path) / (1024 * 1024), 2),
            'products_count': len(list(self.products_path.iterdir())) if self.products_path.exists() else 0,
            'generated_campaigns': len(list(self.generated_path.iterdir())) if self.generated_path.exists() else 0
        }

    def cleanup_generated(self, campaign_name: str = None):
        """
        Clean up generated assets.

        Args:
            campaign_name: Optional specific campaign to clean up (cleans all if not provided)
        """
        if campaign_name:
            campaign_dir = self.generated_path / campaign_name
            if campaign_dir.exists():
                shutil.rmtree(campaign_dir)
                logger.info(f"Cleaned up campaign: {campaign_name}")
        else:
            if self.generated_path.exists():
                shutil.rmtree(self.generated_path)
                self.generated_path.mkdir(parents=True, exist_ok=True)
                logger.info("Cleaned up all generated assets")
