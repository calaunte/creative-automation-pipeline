# Creative Automation Pipeline - CLI Tool

A Python-based command-line tool for automating creative asset generation for social ad campaigns using GenAI.

## Overview

This proof-of-concept tool demonstrates automated creative generation for global social ad campaigns. It accepts campaign briefs, generates or reuses product assets, creates multi-format creatives with text overlays, and performs brand and legal compliance checks.

## Features

### Core Functionality
- ✅ **Campaign Brief Parser**: Accepts JSON/YAML campaign briefs with validation
- ✅ **Multi-Product Support**: Process multiple products in a single campaign
- ✅ **Asset Management**: Intelligent asset reuse and caching
- ✅ **GenAI Image Generation**: Generates missing assets using OpenAI DALL-E 3
- ✅ **Multi-Format Generation**: Creates creatives for 3 aspect ratios (1:1, 9:16, 16:9)
- ✅ **Text Overlay**: Adds campaign messages with brand-aligned styling
- ✅ **Organized Output**: Saves creatives organized by product and aspect ratio

### Quality Assurance (Bonus Features)
- ✅ **Brand Compliance Checks**:
  - Logo detection using computer vision
  - Brand color validation
  - Image resolution verification

- ✅ **Legal Content Checks**:
  - Prohibited word detection
  - Message length validation
  - Compliance reporting

- ✅ **Logging & Reporting**:
  - Comprehensive campaign processing logs
  - JSON reports with compliance details
  - Progress tracking with visual feedback

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- OpenAI API key (for image generation)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd task2-automation-pipeline
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` file** and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

---

## Usage

### Basic Commands

#### 1. Generate Campaign Creatives

**Using a JSON brief**:
```bash
python src/main.py generate examples/campaign_brief_example.json
```

**Using a YAML brief**:
```bash
python src/main.py generate examples/campaign_brief_example.yaml
```

**Specify custom output directory**:
```bash
python src/main.py generate examples/campaign_brief_example.json --output ./my_campaign
```

**Use mock mode** (no API calls, generates placeholder images):
```bash
python src/main.py generate examples/campaign_brief_example.json --mock
```

#### 2. Validate Campaign Brief

```bash
python src/main.py validate examples/campaign_brief_example.json
```

#### 3. View Pipeline Configuration

```bash
python src/main.py info
```

#### 4. Test OpenAI API Connection

```bash
python src/main.py test-api
```

### Campaign Brief Format

#### JSON Format Example

```json
{
  "campaign_name": "summer_refresh_2025",
  "products": [
    {
      "product_id": "energy_drink_001",
      "product_name": "PowerBoost Energy Drink",
      "product_description": "Premium energy drink with natural caffeine...",
      "product_image": null
    },
    {
      "product_id": "protein_bar_002",
      "product_name": "VitaFit Protein Bar",
      "product_description": "High-protein nutrition bar...",
      "product_image": null
    }
  ],
  "target_region": "North America",
  "target_audience": "Active millennials and Gen Z (ages 18-35)...",
  "campaign_message": "Fuel Your Adventure - Discover the perfect energy boost",
  "brand_guidelines": {
    "primary_color": "#0066CC",
    "secondary_color": "#FF6600",
    "font_family": "Arial"
  },
  "localization": {
    "languages": ["en", "es", "fr"],
    "translations": {
      "en": "Fuel Your Adventure...",
      "es": "Alimenta Tu Aventura...",
      "fr": "Alimentez Votre Aventure..."
    }
  },
  "aspect_ratios": ["1:1", "9:16", "16:9"]
}
```

#### Required Fields
- `campaign_name`: Unique identifier for the campaign
- `products`: Array of at least 1 product (required fields: `product_id`, `product_name`)
- `target_region`: Geographic target market
- `target_audience`: Target demographic description
- `campaign_message`: Primary campaign message to overlay on creatives

#### Optional Fields
- `brand_guidelines`: Brand styling preferences
- `localization`: Multi-language support
- `aspect_ratios`: Custom aspect ratios (defaults to 1:1, 9:16, 16:9)

---

## Output Structure

After running the pipeline, outputs are organized as follows:

```
output/
└── campaign_name/
    ├── campaign_report.json          # Summary report with compliance details
    ├── product_id_1/
    │   ├── 1x1/
    │   │   └── product_id_1_1x1.jpg
    │   ├── 9x16/
    │   │   └── product_id_1_9x16.jpg
    │   └── 16x9/
    │       └── product_id_1_16x9.jpg
    └── product_id_2/
        ├── 1x1/
        │   └── product_id_2_1x1.jpg
        ├── 9x16/
        │   └── product_id_2_9x16.jpg
        └── 16x9/
            └── product_id_2_16x9.jpg
```

### Campaign Report

The `campaign_report.json` file contains:
- Products processed count
- Creatives generated count
- List of all creative file paths
- Compliance summary (passed/failed checks)
- Detailed compliance reports for each creative
- Any errors encountered during processing

Example snippet:
```json
{
  "campaign_name": "summer_refresh_2025",
  "products_processed": 2,
  "creatives_generated": 6,
  "compliance_summary": {
    "total_checks": 6,
    "passed": 5,
    "failed": 1
  },
  "compliance_details": { ... }
}
```

---

## Architecture

### Module Overview

```
src/
├── main.py                          # CLI entry point and pipeline orchestration
├── config.py                        # Configuration management
└── modules/
    ├── brief_parser.py              # Campaign brief parsing and validation
    ├── asset_manager.py             # Asset storage and retrieval
    ├── image_generator.py           # GenAI image generation (OpenAI DALL-E)
    ├── creative_generator.py        # Multi-format creative generation
    └── compliance_checker.py        # Brand and legal compliance checks
```

### Pipeline Flow

```
Campaign Brief (JSON/YAML)
    │
    ▼
[1] Brief Parser
    │ - Schema validation
    │ - Data extraction
    │
    ▼
[2] Asset Manager
    │ - Check for existing assets
    │ - Retrieve or mark for generation
    │
    ▼
[3] Image Generator (if needed)
    │ - Generate product images using DALL-E
    │ - Prompt engineering for brand consistency
    │
    ▼
[4] Creative Generator
    │ - Resize to multiple aspect ratios (1:1, 9:16, 16:9)
    │ - Add text overlay with campaign message
    │ - Apply brand styling
    │
    ▼
[5] Compliance Checker
    │ - Brand compliance (logo, colors, resolution)
    │ - Legal checks (prohibited words, message length)
    │
    ▼
[6] Output & Reporting
    │ - Save organized creatives
    │ - Generate compliance report
```

---

## Key Design Decisions

### 1. Modular Architecture
**Decision**: Separate concerns into independent modules (parser, generator, compliance, etc.)

**Rationale**: Enables easier testing, maintenance, and future expansion. Each module can be enhanced or replaced independently.

### 2. Asset Reuse Strategy
**Decision**: Check for existing assets before generating new ones

**Rationale**: Reduces API costs and processing time. Enables consistency across campaigns when reusing product assets.

### 3. OpenAI DALL-E 3 for Image Generation
**Decision**: Use DALL-E 3 as the primary GenAI model

**Rationale**:
- High-quality, photorealistic outputs
- Good prompt adherence for brand consistency
- Commercial licensing suitable for advertising
- Fallback to mock mode for testing without API costs

### 4. Center-Crop Resizing
**Decision**: Center-crop images when resizing to different aspect ratios

**Rationale**: Maintains focal point of the image while ensuring exact aspect ratio compliance for social platforms.

### 5. Compliance as Quality Gate
**Decision**: Run compliance checks after generation but don't block output

**Rationale**: Provides visibility into compliance issues while allowing human review and decision-making.

### 6. JSON/YAML Brief Support
**Decision**: Accept both JSON and YAML formats for campaign briefs

**Rationale**: JSON for programmatic integration, YAML for human readability and manual editing.

---

## Assumptions & Limitations

### Assumptions
1. **OpenAI API Access**: Users have valid OpenAI API key with sufficient credits
2. **English Primary**: Text overlay optimized for English (multi-language supported in briefs)
3. **Standard Aspect Ratios**: Social platforms accept 1:1, 9:16, and 16:9 formats
4. **Brand Guidelines**: Brand colors and fonts provided in brief or config
5. **Local Execution**: Tool runs on local machine or server (not cloud-native yet)

### Limitations
1. **No Video Support**: Only static image creatives (video is future enhancement)
2. **Basic Logo Detection**: Template matching has limitations with stylized/rotated logos
3. **No A/B Variant Generation**: Generates one creative per product/format (not multiple variants)
4. **Limited Font Support**: Uses system fonts; custom brand fonts require manual installation
5. **No Direct Social Platform Publishing**: Saves locally; manual upload to ad platforms required
6. **API Rate Limits**: OpenAI DALL-E has rate limits (60 images/minute for standard tier)
7. **Cost**: DALL-E 3 costs $0.04-$0.08 per image depending on quality/size settings

### Known Issues
1. **Long Campaign Messages**: Very long messages may not fit well on smaller formats
2. **Logo Detection Sensitivity**: May not detect heavily modified or transparent logos
3. **Color Matching**: Brand color detection uses RGB distance (may miss subtle variations)

---

## Examples

### Example 1: Summer Refresh Campaign

**Input**: `examples/campaign_brief_example.json`

**Command**:
```bash
python src/main.py generate examples/campaign_brief_example.json
```

**Output**: 6 creatives (2 products × 3 formats)
- PowerBoost Energy Drink: 1:1, 9:16, 16:9
- VitaFit Protein Bar: 1:1, 9:16, 16:9

**Processing Time**: ~2-3 minutes (with API calls)

### Example 2: Holiday Gift Guide Campaign

**Input**: `examples/campaign_brief_example.yaml`

**Command**:
```bash
python src/main.py generate examples/campaign_brief_example.yaml
```

**Output**: 6 creatives (2 products × 3 formats)
- TechFit Smartwatch Pro: 1:1, 9:16, 16:9
- AudioPure Wireless Earbuds: 1:1, 9:16, 16:9

**Processing Time**: ~2-3 minutes (with API calls)

### Example 3: Mock Mode Testing

**Command**:
```bash
python src/main.py generate examples/campaign_brief_example.json --mock
```

**Output**: 6 placeholder creatives (instant generation, no API calls)

---

## Testing

### Validate Campaign Briefs
```bash
# Test JSON format
python src/main.py validate examples/campaign_brief_example.json

# Test YAML format
python src/main.py validate examples/campaign_brief_example.yaml
```

### Test API Connection
```bash
python src/main.py test-api
```

### Generate with Mock Mode
```bash
python src/main.py generate examples/campaign_brief_example.json --mock
```

---

## Troubleshooting

### Issue: "OPENAI_API_KEY is not set"

**Solution**:
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to the `.env` file
3. Ensure `.env` is in the project root directory

### Issue: "Package not found" errors

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: PIL font errors

**Solution**: The tool falls back to default fonts if custom fonts aren't available. To use Helvetica:
- **macOS**: Font should be available at `/System/Library/Fonts/Helvetica.ttc`
- **Windows**: Install Arial or Helvetica font
- **Linux**: `sudo apt-get install fonts-liberation`

### Issue: OpenCV not working

**Solution**:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: Slow API responses

**Solution**:
- Use `--mock` flag for testing without API calls
- Check OpenAI API status at https://status.openai.com
- Consider using `dall-e-2` in config (faster but lower quality)

---

## Future Enhancements

### Planned Features
1. **Video Creative Generation**: Support for video ads using Runway/Pika APIs
2. **Advanced Variant Generation**: A/B testing variants with different messaging/visuals
3. **Direct Platform Publishing**: Integration with Facebook Ads, Google Ads APIs
4. **Advanced Analytics**: Performance prediction based on historical data
5. **Template Library**: Pre-approved brand templates for faster generation
6. **Batch Processing**: Process multiple campaigns from a directory
7. **Web Interface**: Browser-based UI for non-technical users
8. **Custom Font Support**: Upload and use custom brand fonts
9. **Advanced Localization**: Automatic translation and cultural adaptation

---

## Configuration

### Environment Variables

See `.env.example` for all configurable options:

```bash
# API Configuration
OPENAI_API_KEY=your_api_key_here
IMAGE_MODEL=dall-e-3                    # or dall-e-2
IMAGE_SIZE=1024x1024                   # or 1024x1792, 1792x1024
IMAGE_QUALITY=standard                 # or hd

# Storage
ASSET_STORAGE_PATH=./assets
OUTPUT_PATH=./output

# Brand Compliance
BRAND_LOGO_PATH=./assets/brand/logo.png
BRAND_COLORS=#FF0000,#FFFFFF,#000000

# Legal Compliance
PROHIBITED_WORDS=guarantee,cure,miracle,free

# Formats
ASPECT_RATIOS=1:1,9:16,16:9

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
```

---

## Cost Estimation

### OpenAI DALL-E 3 Pricing (as of 2025)
- **Standard Quality (1024×1024)**: $0.040 per image
- **HD Quality (1024×1024)**: $0.080 per image

### Example Campaign Costs
- **2 products, 3 formats**: 2 images generated = **$0.08 - $0.16**
- **10 products, 3 formats**: 10 images generated = **$0.40 - $0.80**
- **100 products, 3 formats**: 100 images generated = **$4.00 - $8.00**

**Note**: Costs only apply to initial image generation. Subsequent creative format generation (resizing, text overlay) is free.

---

## Dependencies

See `requirements.txt` for complete list:

- **click**: CLI framework
- **Pillow**: Image processing
- **OpenAI**: GenAI image generation
- **PyYAML**: YAML parsing
- **jsonschema**: Brief validation
- **opencv-python**: Computer vision (logo detection)
- **colorama**: Colored CLI output
- **tqdm**: Progress bars
- **requests**: HTTP client
- **python-dotenv**: Environment configuration

---

## License

This is a proof-of-concept project for evaluation purposes.

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review example campaign briefs in `examples/`
3. Run `python src/main.py --help` for command reference

---

## Author

Created by Calaunte
Date: 2025-09-30
