# Creative Automation Pipeline

A Python-based CLI tool for automating creative asset generation for social ad campaigns using GenAI.

**Project Date:** September 30, 2025
**Purpose:** Adobe Forward Deploy Engineer Project

---

## 📋 Project Overview

This project delivers a creative automation pipeline designed for a global consumer goods company launching hundreds of localized social ad campaigns monthly. The solution addresses key business goals:

1. ✅ **Accelerate Campaign Velocity**: Rapidly produce and launch campaigns
2. ✅ **Ensure Brand Consistency**: Maintain global brand guidelines
3. ✅ **Maximize Relevance**: Adapt messaging for local cultures and preferences
4. ✅ **Optimize Marketing ROI**: Improve performance while reducing costs
5. ✅ **Generate Quality Assets**: Automated creative generation with compliance checks

---

## 🗂️ Project Structure

```
creative-automation-pipeline/
│
├── creative-cli/                    # Python CLI Tool
│   ├── src/                         # Source code
│   │   ├── main.py                  # CLI entry point
│   │   ├── config.py                # Configuration
│   │   └── modules/                 # Core modules
│   │       ├── brief_parser.py      # Campaign brief parser
│   │       ├── asset_manager.py     # Asset storage & retrieval
│   │       ├── image_generator.py   # GenAI image generation
│   │       ├── creative_generator.py # Multi-format creative generation
│   │       └── compliance_checker.py # Brand & legal compliance
│   ├── examples/                    # Example campaign briefs
│   ├── assets/                      # Asset storage
│   ├── output/                      # Generated creatives
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Detailed documentation
│
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🔧 Features

### Core Functionality
✅ **Campaign Brief Parser**: Accepts JSON/YAML campaign briefs with validation

✅ **Multi-Product Support**: Process multiple products in a single campaign

✅ **Asset Management**: Intelligent asset reuse and caching

✅ **GenAI Image Generation**: Generates missing assets using OpenAI DALL-E 3

✅ **Multi-Format Generation**: Creates creatives for 3 aspect ratios (1:1, 9:16, 16:9)

✅ **Text Overlay**: Adds campaign messages with brand-aligned styling

✅ **Organized Output**: Saves creatives organized by product and aspect ratio

### Quality Assurance (Bonus)
✅ **Brand Compliance Checks**:
  - Logo detection using computer vision
  - Brand color validation
  - Image resolution verification

✅ **Legal Content Checks**:
  - Prohibited word detection
  - Message length validation
  - Compliance reporting

✅ **Logging & Reporting**:
  - Comprehensive campaign processing logs
  - JSON reports with compliance details
  - Progress tracking with visual feedback

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager
- OpenAI API key (for image generation)

### Installation

```bash
cd creative-cli

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### Quick Start

```bash
# Generate campaign creatives (with real OpenAI API)
python src/main.py generate examples/campaign_brief_example.json

# Generate with mock mode (no API calls, placeholder images)
python src/main.py generate examples/campaign_brief_example.json --mock

# Validate a campaign brief
python src/main.py validate examples/campaign_brief_example.json

# View pipeline configuration
python src/main.py info

# Test OpenAI API connection
python src/main.py test-api
```

---

## 📄 Campaign Brief Format

Campaign briefs can be in JSON or YAML format.

### Required Fields

```json
{
  "campaign_name": "summer_refresh_2025",
  "products": [
    {
      "product_id": "energy_drink_001",
      "product_name": "PowerBoost Energy Drink",
      "product_description": "Premium energy drink...",
      "product_image": null
    }
  ],
  "target_region": "North America",
  "target_audience": "Active millennials and Gen Z...",
  "campaign_message": "Fuel Your Adventure"
}
```

### Optional Fields

- `brand_guidelines`: Brand styling (colors, fonts)
- `localization`: Multi-language translations
- `aspect_ratios`: Custom aspect ratios (defaults to 1:1, 9:16, 16:9)

See `creative-cli/examples/` for complete examples.

---

## 📁 Output Structure

```
output/
└── {campaign_name}/
    ├── campaign_report.json          # Compliance summary
    └── {product_id}/
        ├── 1x1/{product_id}_1x1.jpg
        ├── 9x16/{product_id}_9x16.jpg
        └── 16x9/{product_id}_16x9.jpg
```

**Example**: For a 2-product campaign, you get 6 creative variants (2 products × 3 formats).

---

## 🔄 How It Works

```
Campaign Brief (JSON/YAML)
    │
    ▼
Brief Parser (validate & parse)
    │
    ▼
Asset Manager (check for existing assets)
    │
    ├──> Assets exist? → Reuse them
    └──> Assets missing? → Generate with DALL-E 3
    │
    ▼
Creative Generator
    │ - Resize to 3 aspect ratios (1:1, 9:16, 16:9)
    │ - Add text overlay with campaign message
    │ - Apply brand styling
    │
    ▼
Compliance Checker
    │ - Brand compliance (logo, colors, resolution)
    │ - Legal checks (prohibited words, message length)
    │
    ▼
Output & Report
    │ - Save creatives (organized by product/format)
    │ - Generate campaign_report.json
```

---

## 🔑 Key Design Decisions

1. **OpenAI DALL-E 3**: High-quality, commercially-licensed image generation
2. **Center-crop resizing**: Maintains focal point while meeting exact aspect ratios
3. **Asset reuse strategy**: Checks existing assets before generating new ones (reduces API costs)
4. **Modular architecture**: Independent modules for easy testing and maintenance
5. **Compliance as quality gate**: Runs checks but doesn't block output

---

### Cost Analysis

**OpenAI DALL-E 3 Pricing**:
- Standard quality: $0.04/image
- HD quality: $0.08/image

**Example Campaign Costs**:
- 2-product campaign: 2 images = **$0.08** (standard quality)
- 10-product campaign: 10 images = **$0.40** (standard quality)
- 100-product campaign: 100 images = **$4.00** (standard quality)

**Note**: Costs only apply to initial image generation. Format variants (resizing, text overlay) are free.

---

## ⚙️ Configuration

All configuration is managed via `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
IMAGE_MODEL=dall-e-3                    # or dall-e-2
IMAGE_SIZE=1024x1024                   # or 1024x1792, 1792x1024
IMAGE_QUALITY=standard                 # or hd
ASPECT_RATIOS=1:1,9:16,16:9
BRAND_COLORS=#FF0000,#FFFFFF,#000000
PROHIBITED_WORDS=guarantee,cure,miracle,free
```

---

## 🛠️ Troubleshooting

### OpenAI API Billing Error

**Error**: `billing_hard_limit_reached`

**Solutions**:
1. Use `--mock` flag for testing without API calls
2. Place existing images in `assets/products/{product_id}/` for reuse
3. Add billing to your OpenAI account at https://platform.openai.com/account/billing

### Schema Validation Errors

Campaign briefs must have `product_description` and `product_image` as nullable fields. Check `examples/` for valid format.

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

---

## 📖 Documentation

- **Main README**: This file
- **CLI Tool README**: `creative-cli/README.md` - Detailed usage guide
- **CLAUDE.md**: Guidance for Claude Code instances
- **Examples**: `creative-cli/examples/` - Sample campaign briefs

---

## 🎯 Success Criteria

✅ Campaign brief parser (JSON/YAML)
✅ Multi-product support (2+ products)
✅ Asset management and reuse
✅ GenAI image generation (OpenAI DALL-E 3)
✅ Multi-format creatives (1:1, 9:16, 16:9)
✅ Text overlay with campaign messages
✅ Organized output structure
✅ **Bonus**: Brand compliance checks
✅ **Bonus**: Legal content checks
✅ **Bonus**: Comprehensive logging & reporting

---

## 🔮 Future Enhancements

### Short-term (3-6 months)
1. Video creative generation (RunwayML/Pika)
2. A/B variant testing
3. Advanced brand detection
4. Direct platform publishing (Facebook Ads, Google Ads)

### Long-term (6-12 months)
1. Predictive analytics (ML models for campaign performance)
2. Dynamic creative optimization
3. Self-service web UI
4. Multi-tenant support

---

## 🤝 Support

For questions or issues:
1. Check `creative-cli/README.md` for detailed documentation
2. Review example campaign briefs in `creative-cli/examples/`
3. See `CLAUDE.md` for architecture details

---

## 📜 License

This is a proof-of-concept project created for evaluation purposes.

---

## 🙏 Technologies Used

- **OpenAI DALL-E 3** - GenAI image generation
- **Python 3.10+** - Core implementation
- **Pillow/OpenCV** - Image processing and validation
- **Click** - CLI framework
- **jsonschema** - Brief validation

---

**End of Documentation**
