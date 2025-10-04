# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Creative Automation Pipeline** for generating social media ad campaigns at scale. The system consists of a Python CLI tool (`creative-cli/`) that:
1. Parses campaign briefs (JSON/YAML)
2. Generates or reuses product images via OpenAI DALL-E 3
3. Creates multi-format creatives (1:1, 9:16, 16:9 aspect ratios)
4. Adds text overlays with campaign messages
5. Performs brand and legal compliance checks

**Purpose**: Adobe Forward Deploy Engineer Project proof-of-concept.

## Essential Commands

### Setup
```bash
cd creative-cli
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

### Running the Pipeline

**Generate creatives (with real OpenAI API)**:
```bash
python src/main.py generate examples/campaign_brief_example.json
```

**Mock mode (no API calls, uses placeholder images)**:
```bash
python src/main.py generate examples/campaign_brief_example.json --mock
```

**Validate campaign brief**:
```bash
python src/main.py validate examples/campaign_brief_example.json
```

**Test OpenAI API connection**:
```bash
python src/main.py test-api
```

**View configuration**:
```bash
python src/main.py info
```

## Architecture

### Pipeline Flow
```
Campaign Brief → Brief Parser → Asset Manager → Image Generator (DALL-E 3)
→ Creative Generator (resize + text overlay) → Compliance Checker
→ Output (organized by product/format)
```

### Key Components

**`src/main.py`**: CLI orchestrator using Click framework. Entry point for all commands.

**`src/config.py`**: Centralized configuration loaded from `.env`. Uses class methods for validation and directory setup.

**`src/modules/brief_parser.py`**:
- Parses and validates JSON/YAML campaign briefs using jsonschema
- Key class: `CampaignBrief` with schema validation
- **Important**: `product_description` and `product_image` fields accept `null` values

**`src/modules/asset_manager.py`**:
- Manages asset storage in `assets/products/{product_id}/`
- Implements intelligent asset reuse (checks before generating)
- Stores generated images in `assets/generated/`

**`src/modules/image_generator.py`**:
- `ImageGenerator`: Real DALL-E 3 integration via OpenAI SDK
- `MockImageGenerator`: Fallback that creates placeholder images (PIL-based with minimal PNG fallback)
- **Critical**: Mock mode always returns valid image data, even without PIL

**`src/modules/creative_generator.py`**:
- Resizes images to multiple aspect ratios using center-crop strategy
- Adds text overlays with semi-transparent backgrounds
- Uses PIL for image manipulation
- Outputs to `output/{campaign_name}/{product_id}/{aspect_ratio}/`

**`src/modules/compliance_checker.py`**:
- Brand checks: logo detection (OpenCV template matching), color validation, resolution
- Legal checks: prohibited words, message length
- Returns `ComplianceReport` objects with pass/fail status

### Data Flow

1. **Input**: `examples/*.json` or `*.yaml` campaign briefs
2. **Asset Storage**: `assets/products/{product_id}/*.{jpg,png}`
3. **Output**: `output/{campaign_name}/{product_id}/{aspect_ratio}/*.jpg`
4. **Reports**: `output/{campaign_name}/campaign_report.json`

### Configuration via .env

Required:
- `OPENAI_API_KEY`: OpenAI API key for DALL-E 3

Optional:
- `IMAGE_MODEL`: Default `dall-e-3`
- `IMAGE_SIZE`: Default `1024x1024`
- `IMAGE_QUALITY`: `standard` or `hd`
- `ASPECT_RATIOS`: Default `1:1,9:16,16:9`
- `BRAND_COLORS`: Comma-separated hex colors
- `PROHIBITED_WORDS`: Comma-separated words for legal checks

## Common Issues & Solutions

### Schema Validation Errors
Campaign briefs must have `product_description` and `product_image` as nullable fields (`type: ["string", "null"]`). If validation fails, check `brief_parser.py` SCHEMA definition.

### OpenAI API Billing Errors
If you see "billing_hard_limit_reached":
- Use `--mock` flag for testing without API calls
- Or place existing images in `assets/products/{product_id}/` for reuse

### Mock Image Generation
The `MockImageGenerator` has two fallback mechanisms:
1. Creates 1024x1024 placeholder with PIL
2. Returns minimal valid PNG binary if PIL fails

### Missing Dependencies
All image processing requires:
- Pillow (PIL)
- opencv-python (for logo detection)
- openai (for DALL-E 3)

## Key Design Patterns

### Asset Reuse Strategy
Before calling OpenAI API, `AssetManager.get_product_asset()` checks `assets/products/{product_id}/` for existing images. This saves API costs.

### Center-Crop Resizing
`CreativeGenerator._resize_and_crop()` maintains image focal point by:
1. Calculating target aspect ratio
2. Cropping from center
3. Resizing to exact dimensions

### Compliance as Quality Gate
Compliance checks run after generation but don't block output. Reports are stored in `campaign_report.json` for review.

### Mock Mode vs Real Mode
Pipeline automatically falls back to mock mode if:
- No `OPENAI_API_KEY` in config
- API validation fails
This ensures the pipeline always demonstrates functionality.

## Output Structure

```
output/
└── {campaign_name}/
    ├── campaign_report.json          # Compliance summary
    └── {product_id}/
        ├── 1x1/{product_id}_1x1.jpg
        ├── 9x16/{product_id}_9x16.jpg
        └── 16x9/{product_id}_16x9.jpg
```

## Campaign Brief Schema

Required fields:
- `campaign_name`: string
- `products`: array of objects with `product_id`, `product_name`
- `target_region`: string
- `target_audience`: string
- `campaign_message`: string

Optional fields:
- `brand_guidelines`: object with `primary_color`, `secondary_color`, `font_family`
- `localization`: object with `languages`, `translations`
- `aspect_ratios`: array of strings like `["1:1", "9:16", "16:9"]`

## Logging

All operations log to:
- Console (colored output via colorama)
- `creative_pipeline.log` in project root

Log levels controlled by `LOG_LEVEL` in `.env` (default: INFO).

## Testing Without API Key

1. Use `--mock` flag for all generate commands
2. Or place test images in `assets/products/{product_id}/product.jpg`
3. Pipeline will detect and reuse existing assets

## API Cost Considerations

- DALL-E 3 Standard: $0.04/image
- DALL-E 3 HD: $0.08/image
- Pipeline generates 1 image per product (reused across formats)
- Example: 2-product campaign = 2 images = $0.08 (standard quality)
