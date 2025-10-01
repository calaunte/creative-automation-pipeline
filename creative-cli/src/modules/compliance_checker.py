"""
Compliance Checker Module
Handles brand compliance and legal content checks for creative assets.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ComplianceReport:
    """Represents a compliance check report."""

    def __init__(self):
        """Initialize empty compliance report."""
        self.brand_checks = {}
        self.legal_checks = {}
        self.warnings = []
        self.errors = []
        self.passed = True

    def add_brand_check(self, check_name: str, passed: bool, details: str = None):
        """Add a brand compliance check result."""
        self.brand_checks[check_name] = {
            'passed': passed,
            'details': details
        }
        if not passed:
            self.passed = False
            self.errors.append(f"Brand check failed: {check_name} - {details}")

    def add_legal_check(self, check_name: str, passed: bool, details: str = None):
        """Add a legal compliance check result."""
        self.legal_checks[check_name] = {
            'passed': passed,
            'details': details
        }
        if not passed:
            self.passed = False
            self.errors.append(f"Legal check failed: {check_name} - {details}")

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'passed': self.passed,
            'brand_checks': self.brand_checks,
            'legal_checks': self.legal_checks,
            'warnings': self.warnings,
            'errors': self.errors
        }

    def __str__(self) -> str:
        """String representation of the report."""
        status = "PASSED" if self.passed else "FAILED"
        return (f"Compliance Report: {status}\n"
                f"Brand Checks: {len(self.brand_checks)}\n"
                f"Legal Checks: {len(self.legal_checks)}\n"
                f"Warnings: {len(self.warnings)}\n"
                f"Errors: {len(self.errors)}")


class ComplianceChecker:
    """Checks creative assets for brand and legal compliance."""

    def __init__(
        self,
        prohibited_words: List[str] = None,
        brand_colors: List[str] = None,
        logo_path: Path = None
    ):
        """
        Initialize compliance checker.

        Args:
            prohibited_words: List of words that are not allowed
            brand_colors: List of approved brand colors (hex format)
            logo_path: Path to brand logo for detection
        """
        self.prohibited_words = [word.lower() for word in (prohibited_words or [])]
        self.brand_colors = brand_colors or []
        self.logo_path = logo_path

    def check_creative(
        self,
        image_path: Path,
        campaign_message: str,
        strict: bool = False
    ) -> ComplianceReport:
        """
        Perform comprehensive compliance check on a creative asset.

        Args:
            image_path: Path to the creative image
            campaign_message: Campaign message text
            strict: If True, treat warnings as errors

        Returns:
            ComplianceReport with check results
        """
        report = ComplianceReport()

        # Legal content checks
        self._check_prohibited_words(campaign_message, report)
        self._check_message_length(campaign_message, report)

        # Brand compliance checks
        if image_path.exists():
            self._check_image_quality(image_path, report)
            if self.logo_path and self.logo_path.exists():
                self._check_logo_presence(image_path, report)
            if self.brand_colors:
                self._check_brand_colors(image_path, report)

        logger.info(f"Compliance check completed: {report}")
        return report

    def _check_prohibited_words(self, text: str, report: ComplianceReport):
        """
        Check for prohibited words in campaign message.

        Args:
            text: Campaign message text
            report: ComplianceReport to update
        """
        if not text:
            return

        text_lower = text.lower()
        found_words = []

        for word in self.prohibited_words:
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower):
                found_words.append(word)

        if found_words:
            report.add_legal_check(
                'prohibited_words',
                False,
                f"Found prohibited words: {', '.join(found_words)}"
            )
        else:
            report.add_legal_check(
                'prohibited_words',
                True,
                "No prohibited words found"
            )

    def _check_message_length(self, text: str, report: ComplianceReport):
        """
        Check if campaign message length is appropriate.

        Args:
            text: Campaign message text
            report: ComplianceReport to update
        """
        if not text:
            report.add_warning("Campaign message is empty")
            return

        max_length = 200  # Reasonable limit for social ads
        min_length = 10

        text_length = len(text)

        if text_length > max_length:
            report.add_warning(
                f"Campaign message is too long ({text_length} chars, max {max_length})"
            )
        elif text_length < min_length:
            report.add_warning(
                f"Campaign message is too short ({text_length} chars, min {min_length})"
            )
        else:
            report.add_legal_check(
                'message_length',
                True,
                f"Message length is appropriate ({text_length} chars)"
            )

    def _check_image_quality(self, image_path: Path, report: ComplianceReport):
        """
        Check image quality metrics.

        Args:
            image_path: Path to image
            report: ComplianceReport to update
        """
        try:
            img = Image.open(image_path)
            width, height = img.size

            # Check minimum resolution
            min_dimension = 800
            if width < min_dimension or height < min_dimension:
                report.add_brand_check(
                    'image_resolution',
                    False,
                    f"Image resolution too low ({width}x{height}, min {min_dimension}px)"
                )
            else:
                report.add_brand_check(
                    'image_resolution',
                    True,
                    f"Image resolution acceptable ({width}x{height})"
                )

            # Check aspect ratio is reasonable
            aspect_ratio = width / height
            if aspect_ratio > 5 or aspect_ratio < 0.2:
                report.add_warning(
                    f"Unusual aspect ratio ({width}:{height})"
                )

        except Exception as e:
            logger.error(f"Failed to check image quality: {e}")
            report.add_warning(f"Could not analyze image quality: {e}")

    def _check_logo_presence(self, image_path: Path, report: ComplianceReport):
        """
        Check if brand logo is present in the image (basic template matching).

        Args:
            image_path: Path to creative image
            report: ComplianceReport to update
        """
        try:
            # Load images
            img = cv2.imread(str(image_path))
            logo = cv2.imread(str(self.logo_path))

            if img is None or logo is None:
                report.add_warning("Could not load images for logo detection")
                return

            # Convert to grayscale
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            logo_gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)

            # Resize logo if too large relative to image
            img_h, img_w = img_gray.shape
            logo_h, logo_w = logo_gray.shape

            if logo_h > img_h * 0.5 or logo_w > img_w * 0.5:
                scale = min(img_h / logo_h, img_w / logo_w) * 0.3
                new_w = int(logo_w * scale)
                new_h = int(logo_h * scale)
                logo_gray = cv2.resize(logo_gray, (new_w, new_h))

            # Template matching
            result = cv2.matchTemplate(img_gray, logo_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Threshold for match (lower threshold for flexibility)
            threshold = 0.4

            if max_val >= threshold:
                report.add_brand_check(
                    'logo_presence',
                    True,
                    f"Logo detected (confidence: {max_val:.2f})"
                )
            else:
                # Don't fail, just warn (logo might be stylized differently)
                report.add_warning(
                    f"Logo not clearly detected (confidence: {max_val:.2f}, threshold: {threshold})"
                )

        except Exception as e:
            logger.error(f"Failed to check logo presence: {e}")
            report.add_warning(f"Could not perform logo detection: {e}")

    def _check_brand_colors(self, image_path: Path, report: ComplianceReport):
        """
        Check if brand colors are present in the image.

        Args:
            image_path: Path to creative image
            report: ComplianceReport to update
        """
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')

            # Get dominant colors
            pixels = np.array(img)
            pixels = pixels.reshape(-1, 3)

            # Sample pixels for performance
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]

            # Get unique colors
            unique_colors = np.unique(pixels, axis=0)

            # Convert brand colors to RGB
            brand_colors_rgb = [self._hex_to_rgb(color) for color in self.brand_colors]

            # Check if any brand color is present (with some tolerance)
            tolerance = 30  # RGB distance tolerance
            found_colors = []

            for brand_color in brand_colors_rgb:
                for pixel_color in unique_colors:
                    distance = np.linalg.norm(np.array(brand_color) - np.array(pixel_color))
                    if distance <= tolerance:
                        found_colors.append(brand_color)
                        break

            if found_colors:
                report.add_brand_check(
                    'brand_colors',
                    True,
                    f"Found {len(found_colors)} brand colors in image"
                )
            else:
                report.add_warning(
                    "Brand colors not prominently detected in image"
                )

        except Exception as e:
            logger.error(f"Failed to check brand colors: {e}")
            report.add_warning(f"Could not analyze brand colors: {e}")

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., '#FF0000')

        Returns:
            (R, G, B) tuple
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def batch_check(
        self,
        creative_paths: List[Path],
        campaign_message: str
    ) -> Dict[Path, ComplianceReport]:
        """
        Perform compliance checks on multiple creatives.

        Args:
            creative_paths: List of creative image paths
            campaign_message: Campaign message text

        Returns:
            Dictionary mapping paths to compliance reports
        """
        reports = {}

        for path in creative_paths:
            logger.info(f"Checking compliance for: {path}")
            reports[path] = self.check_creative(path, campaign_message)

        return reports
