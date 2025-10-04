"""
Creative Automation Pipeline - Main CLI Application
Command-line tool for automating creative asset generation for social ad campaigns.
"""

import sys
import logging
from pathlib import Path
import click
from colorama import init, Fore, Style
import json
from tqdm import tqdm

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from modules.brief_parser import BriefParser
from modules.asset_manager import AssetManager
from modules.image_generator import ImageGenerator, MockImageGenerator
from modules.creative_generator import CreativeGenerator
from modules.compliance_checker import ComplianceChecker

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('creative_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CreativeAutomationPipeline:
    """Main pipeline orchestrator for creative automation."""

    def __init__(self, use_mock: bool = False):
        """
        Initialize the pipeline.

        Args:
            use_mock: If True, use mock image generator (no API calls)
        """
        self.config = Config
        self.asset_manager = AssetManager(self.config.ASSET_STORAGE_PATH)

        # Initialize image generator
        if use_mock:
            self.image_generator = MockImageGenerator()
            logger.info("Using mock image generator (no API calls)")
        else:
            try:
                self.config.validate()
                self.image_generator = ImageGenerator(
                    api_key=self.config.OPENAI_API_KEY,
                    model=self.config.IMAGE_MODEL,
                    size=self.config.IMAGE_SIZE,
                    quality=self.config.IMAGE_QUALITY
                )
            except ValueError as e:
                logger.warning(f"Cannot use OpenAI API: {e}. Falling back to mock mode.")
                self.image_generator = MockImageGenerator()

        self.creative_generator = CreativeGenerator()
        self.compliance_checker = ComplianceChecker(
            prohibited_words=self.config.PROHIBITED_WORDS,
            brand_colors=self.config.BRAND_COLORS,
            logo_path=self.config.BRAND_LOGO_PATH
        )

    def process_campaign(self, brief_path: str, output_dir: str = None) -> dict:
        """
        Process a campaign brief and generate creative assets.

        Args:
            brief_path: Path to campaign brief file (JSON or YAML)
            output_dir: Optional custom output directory

        Returns:
            Dictionary with processing results
        """
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}Creative Automation Pipeline")
        print(f"{Fore.CYAN}{'=' * 70}\n")

        results = {
            'campaign_name': None,
            'products_processed': 0,
            'creatives_generated': [],
            'compliance_reports': {},
            'errors': []
        }

        try:
            # Step 1: Parse campaign brief
            print(f"{Fore.YELLOW}Step 1: Parsing campaign brief...")
            brief = BriefParser.parse(brief_path)
            results['campaign_name'] = brief.campaign_name
            print(f"{Fore.GREEN}✓ Campaign: {brief.campaign_name}")
            print(f"  Products: {len(brief.products)}")
            print(f"  Region: {brief.target_region}")
            print(f"  Audience: {brief.target_audience}\n")

            # Step 2: Set up output directory
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = self.config.OUTPUT_PATH / brief.campaign_name

            output_path.mkdir(parents=True, exist_ok=True)

            # Step 3: Process each product
            print(f"{Fore.YELLOW}Step 2: Processing products...")

            for product in tqdm(brief.products, desc="Products", unit="product"):
                try:
                    product_results = self._process_product(
                        product,
                        brief,
                        output_path
                    )
                    results['creatives_generated'].extend(product_results['creatives'])
                    results['compliance_reports'].update(product_results['compliance'])
                    results['products_processed'] += 1

                except Exception as e:
                    error_msg = f"Failed to process product {product['product_id']}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

            # Step 4: Generate summary report
            print(f"\n{Fore.YELLOW}Step 3: Generating summary report...")
            self._generate_report(results, output_path)

            # Print summary
            print(f"\n{Fore.CYAN}{'=' * 70}")
            print(f"{Fore.GREEN}✓ Campaign Processing Complete!")
            print(f"{Fore.CYAN}{'=' * 70}")
            print(f"Products processed: {results['products_processed']}")
            print(f"Creatives generated: {len(results['creatives_generated'])}")
            print(f"Output directory: {output_path}")
            print(f"{Fore.CYAN}{'=' * 70}\n")

            return results

        except Exception as e:
            error_msg = f"Campaign processing failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            print(f"\n{Fore.RED}✗ Error: {error_msg}\n")
            return results

    def _process_product(self, product: dict, brief, output_path: Path) -> dict:
        """Process a single product and generate creatives."""
        product_id = product['product_id']
        product_name = product['product_name']
        product_description = product.get('product_description', '')

        print(f"\n  {Fore.CYAN}Processing: {product_name} ({product_id})")

        results = {
            'creatives': [],
            'compliance': {}
        }

        # Check for existing assets
        existing_asset = self.asset_manager.get_product_asset(product_id)

        if existing_asset:
            print(f"  {Fore.GREEN}✓ Using existing asset: {existing_asset.name}")
            with open(existing_asset, 'rb') as f:
                image_data = f.read()
        else:
            # Generate new asset using GenAI
            print(f"  {Fore.YELLOW}⚡ Generating new asset with AI...")
            image_data = self.image_generator.generate_product_image(
                product_name=product_name,
                product_description=product_description,
                target_audience=brief.target_audience,
                campaign_message=brief.campaign_message,
                region=brief.target_region,
                style_guidelines=brief.brand_guidelines
            )

            if not image_data:
                raise Exception("Failed to generate image")

            # Save generated image to assets/products folder for future reuse across campaigns
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_data)
                tmp_path = tmp_file.name

            saved_path = self.asset_manager.save_product_asset(
                product_id=product_id,
                asset_path=tmp_path,
                asset_name='product.png'
            )

            # Clean up temp file
            Path(tmp_path).unlink()

            # Get relative path for display
            try:
                display_path = saved_path.relative_to(self.config.BASE_DIR)
            except ValueError:
                display_path = saved_path

            print(f"  {Fore.GREEN}✓ Generated new asset (saved to {display_path})")

        # Generate multi-format creatives
        print(f"  {Fore.YELLOW}Creating format variants...")

        # Parse aspect ratios from brief or use config defaults
        aspect_ratios = [
            tuple(map(int, ratio.split(':')))
            for ratio in brief.aspect_ratios
        ]

        product_output_path = output_path / product_id
        product_output_path.mkdir(parents=True, exist_ok=True)

        creative_paths = self.creative_generator.generate_multi_format(
            source_image=image_data,
            aspect_ratios=aspect_ratios,
            campaign_message=brief.campaign_message,
            product_name=product_id,
            output_base_path=product_output_path,
            brand_color=brief.brand_guidelines.get('primary_color')
        )

        results['creatives'] = creative_paths

        # Compliance checks
        print(f"  {Fore.YELLOW}Running compliance checks...")
        for creative_path in creative_paths:
            compliance_report = self.compliance_checker.check_creative(
                creative_path,
                brief.campaign_message
            )
            results['compliance'][str(creative_path)] = compliance_report

            status = f"{Fore.GREEN}✓ PASSED" if compliance_report.passed else f"{Fore.RED}✗ FAILED"
            print(f"    {creative_path.name}: {status}")

        print(f"  {Fore.GREEN}✓ Completed: {len(creative_paths)} variants generated")

        return results

    def _generate_report(self, results: dict, output_path: Path):
        """Generate a summary report of the campaign processing."""
        report_path = output_path / 'campaign_report.json'

        # Convert compliance reports to dictionaries
        compliance_dict = {}
        for path, report in results['compliance_reports'].items():
            compliance_dict[str(path)] = report.to_dict()

        # Convert Path objects to strings for JSON serialization
        creatives_list = [str(p) for p in results['creatives_generated']]

        report_data = {
            'campaign_name': results['campaign_name'],
            'products_processed': results['products_processed'],
            'creatives_generated': len(creatives_list),
            'creative_paths': creatives_list,
            'compliance_summary': {
                'total_checks': len(compliance_dict),
                'passed': sum(1 for r in compliance_dict.values() if r['passed']),
                'failed': sum(1 for r in compliance_dict.values() if not r['passed'])
            },
            'compliance_details': compliance_dict,
            'errors': results['errors']
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"  {Fore.GREEN}✓ Report saved: {report_path}")


# CLI Commands
@click.group()
def cli():
    """Creative Automation Pipeline CLI"""
    pass


@cli.command()
@click.argument('brief_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output directory')
@click.option('--mock', is_flag=True, help='Use mock image generator (no API calls)')
def generate(brief_path, output, mock):
    """Generate creative assets from a campaign brief."""
    pipeline = CreativeAutomationPipeline(use_mock=mock)
    pipeline.process_campaign(brief_path, output)


@cli.command()
@click.argument('brief_path', type=click.Path(exists=True))
def validate(brief_path):
    """Validate a campaign brief file."""
    print(f"\n{Fore.CYAN}Validating campaign brief: {brief_path}\n")

    try:
        brief = BriefParser.parse(brief_path)
        print(f"{Fore.GREEN}✓ Campaign brief is valid!")
        print(f"\nCampaign: {brief.campaign_name}")
        print(f"Products: {len(brief.products)}")
        print(f"Region: {brief.target_region}")
        print(f"Target Audience: {brief.target_audience}")
        print(f"Message: {brief.campaign_message[:100]}...\n")
    except Exception as e:
        print(f"{Fore.RED}✗ Validation failed: {e}\n")
        sys.exit(1)


@cli.command()
def info():
    """Display pipeline configuration and status."""
    print(f"\n{Fore.CYAN}Creative Automation Pipeline - Configuration\n")

    storage_info = AssetManager(Config.ASSET_STORAGE_PATH).get_storage_info()

    print(f"Storage Path: {storage_info['storage_path']}")
    print(f"Total Size: {storage_info['total_size_mb']} MB")
    print(f"Products: {storage_info['products_count']}")
    print(f"Generated Campaigns: {storage_info['generated_campaigns']}")
    print(f"\nAspect Ratios: {', '.join([f'{w}:{h}' for w, h in Config.ASPECT_RATIOS])}")
    print(f"Image Model: {Config.IMAGE_MODEL}")
    print(f"Image Size: {Config.IMAGE_SIZE}")
    print(f"\nProhibited Words: {', '.join(Config.PROHIBITED_WORDS)}")
    print(f"Brand Colors: {', '.join(Config.BRAND_COLORS)}\n")


@cli.command()
def test_api():
    """Test OpenAI API connection."""
    print(f"\n{Fore.CYAN}Testing OpenAI API connection...\n")

    try:
        Config.validate()
        generator = ImageGenerator(
            api_key=Config.OPENAI_API_KEY,
            model=Config.IMAGE_MODEL
        )

        if generator.test_connection():
            print(f"{Fore.GREEN}✓ API connection successful!\n")
        else:
            print(f"{Fore.RED}✗ API connection failed\n")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    cli()
