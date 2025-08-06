# Code to PDF Generator

A Python script that generates PDF files containing **code listings** from your project files. It scans your codebase, finds all supported code files, and creates a PDF document with the complete source code listings formatted for easy reading.

**What it does:**
- Scans your project directory for code files
- Creates a PDF with all your source code listings
- Preserves exact formatting and indentation
- Tracks processed files to avoid duplicates
- Supports 20+ programming languages and file types
- **NEW**: Smart page limiting with intelligent file selection
- **NEW**: Exact page counting and reporting
- **NEW**: Flexible page limits (allows 2-3 extra pages for better utilization)
- **NEW**: AI-powered summary generation using Anthropic API

## Features

- ✅ **Code Listings**: Creates PDF with complete source code listings from your project
- ✅ **Perfect Code Formatting**: Preserves exact original formatting with zero padding
- ✅ **Relative Paths**: Shows clean relative paths instead of long absolute paths
- ✅ **Smart Ignore File**: Track and skip already processed files with wildcard patterns
- ✅ **Flexible Configuration**: Customizable via config file and command line arguments
- ✅ **Long Line Handling**: Automatically wraps long lines while preserving indentation
- ✅ **Smart Page Limiting**: Intelligently selects files to maximize page utilization
- ✅ **Exact Page Counting**: Shows precise page count of generated PDF
- ✅ **Flexible Limits**: Allows 2-3 extra pages beyond limit for better value
- ✅ **Smart File Selection**: Skips oversized files and finds better fits

## Quick Start

### Installation

```bash
# Install dependencies
pip3 install -r requirements.txt
```

### Basic Usage

```bash
# Copy the sample config file first
cp config_sample.json config.json

# Generate PDF with default settings (10 pages)
python3 generate_code_pdf.py

# Generate PDF with custom filename and pages
python3 generate_code_pdf.py --filename my_code.pdf --pages 20

# Generate PDF with custom title and max files
python3 generate_code_pdf.py --title "My Project Code" --filename project.pdf --pages 15 --max-files 10

# Process all files (ignore the ignore file)
python3 generate_code_pdf.py --no-ignore --filename all_files.pdf

# Update ignore file with processed files
python3 generate_code_pdf.py --update-ignore --filename processed.pdf

# Show current configuration
python3 generate_code_pdf.py --show-config
```

## Smart Page Limiting

The script now features intelligent page management:

- **Target Page Limit**: Respects your specified page limit (e.g., 20 pages)
- **Flexible Overrun**: Allows 2-3 extra pages for better utilization
- **Smart File Selection**: Skips files that would exceed by too much
- **Better Value**: Instead of getting 16 pages when you want 20, you get 22-23 pages
- **Exact Reporting**: Shows precise page count of generated PDF

### Example Output

```
Including file assets/common/stylus/settings/optimize.styl - will exceed 20 pages by 3 pages (estimated 23 pages)
Skipping file assets/common/stylus/settings/variables.styl - would exceed 20 pages by too much (estimated 27 pages), trying next file...
PDF generated successfully: output/my_code.pdf
Total pages generated: 23
Files processed and added to PDF: 8
```

## AI-Powered Summary Generation

The script now supports AI-powered summary generation using the Anthropic API:

- **Intelligent Analysis**: AI analyzes file types, names, and structure to create contextual summaries
- **Fallback Support**: If AI is unavailable, falls back to rule-based summaries
- **Descriptive Format**: Generates detailed summaries like "Added React components for user interface. Added new 15 pages."
- **Automatic Integration**: Works seamlessly with existing functionality

### Setup:
1. Install the anthropic package: `pip3 install anthropic`
2. Add your API key to `config.json` (see API Key Setup section below)
3. Run the script normally - AI summaries will be generated automatically

**Alternative**: You can also set the environment variable: `export ANTHROPIC_API_KEY="your-api-key-here"`

### Example AI Summaries:
- **Web Project**: "Added React components for user interface. Added new 15 pages."
- **Mobile Project**: "Added React Native mobile application code. Added new 8 pages."
- **Backend Project**: "Added Python backend API functions. Added new 12 pages."
- **Mixed Project**: "Added full-stack web application components. Added new 20 pages."

### Fallback Behavior:
If no API key is set or AI fails, the script automatically uses rule-based summaries:

**API Key Missing:**
```
Warning: ANTHROPIC_API_KEY not found in config or environment. Using rule-based summary.
Suggested summary: 22 Pug templates, 1 Markdown, 1 JSON config. 14 pages. UI components included.
```

**API Overload (Error 529):**
```
API overloaded, retrying in 2 seconds... (attempt 1/3)
API overloaded, retrying in 4 seconds... (attempt 2/3)
API still overloaded after 3 attempts. Using rule-based summary.
```

**Other API Errors:**
```
Error calling Anthropic API: [error details]. Using rule-based summary.
```

### AI Summary Format:
The AI generates summaries in a consistent format: "Added [technology/component type] [purpose/functionality]. Added new [X] pages."

**Examples:**
- "Added Stylus/Pug styling components for buttons, forms, checkboxes and sprites. Added new 12 pages."
- "Added Pug template components for HTML markup generation and layout structure. Added new 25 pages."
- "Added React components for user interface. Added new 15 pages."
- "Added Python backend API functions. Added new 8 pages."

### Multi-Language Support:
The AI can generate summaries in multiple languages simultaneously. Configure the `languages` array in your config:

```json
"languages": ["en", "ru", "pl", "es", "de"]
```

**Supported Languages:**
- **`en`**: English (default)
- **`ru`**: Russian (Русский)
- **`pl`**: Polish (Polski)
- **`es`**: Spanish (Español)
- **`de`**: German (Deutsch)

**Multi-Language Example:**
```
Summary [EN]: Added Stylus/Pug styling components for design system and UI elements. Added new 9 pages.
Summary [RU]: Добавлены Stylus/Pug стили и шаблоны для оформления базовых UI элементов. Добавлено новых 9 страниц.
Summary [PL]: Dodano style Stylus i szablony Pug dla przewodnika stylów i komponentów UI. Dodano nowych 9 stron.
```

**Smart Translation Process:**
- **English Analysis**: AI first analyzes code files in English for accurate technical understanding
- **Multi-Language Translation**: Then translates to requested languages with proper technical terminology
- **Format Consistency**: Maintains exact format across all languages while preserving technical accuracy
- **Page Count Preservation**: Keeps page numbers unchanged across all language versions

### AI Configuration Options:
You can customize AI behavior in your `config.json`:
```json
"ai": {
  "anthropic_api_key": "your-api-key-here",
  "enable_ai_summary": true,
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 50,
  "temperature": 0.3,
  "languages": ["en"]
}
```

- **`anthropic_api_key`**: Your Anthropic API key (required for AI summaries)
- **`enable_ai_summary`**: Set to `false` to disable AI summaries and use only rule-based summaries
- **`model`**: Choose different Anthropic models (default: claude-3-5-sonnet-20241022)
- **`max_tokens`**: Control response length (default: 50)
- **`temperature`**: Control creativity (0.0 = deterministic, 1.0 = very creative, default: 0.3)
- **`languages`**: Array of language codes for multi-language summaries (default: ["en"])
- **`max_retries`**: Number of retry attempts for API overload errors (default: 3)
- **`retry_delay`**: Initial delay in seconds between retries, doubles each attempt (default: 2)

### API Key Setup:
1. **Config File Method** (Recommended): Add your API key to `config.json`:
   ```json
   "ai": {
     "anthropic_api_key": "sk-ant-api03-your-key-here"
   }
   ```

2. **Environment Variable Method**: Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
   ```

**Note**: The config file method takes precedence over environment variables.

## Detailed Usage

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--ignore-file` | Path to ignore file (overrides config) | From config or `ignore.txt` |
| `--title` | PDF title (overrides config) | From config or "Code Listing" |
| `--filename` | Output filename (overrides config) | From config or "code_listing.pdf" |
| `--output-folder` | Output folder path (overrides config) | From config or "output/" |
| `--pages` | Number of pages to generate (overrides config) | From config or 10 |
| `--max-files` | Maximum number of files to include | No limit |
| `--code-folder` | Code folder path (overrides config) | From config or "../" |
| `--no-ignore` | Process all files, ignoring ignore file | False |
| `--update-ignore` | Update ignore file with processed files | From config or False |
| `--show-config` | Show current configuration and exit | False |

## Configuration

**Important**: The script requires a `config.json` file to run. Copy `config_sample.json` to `config.json` and modify as needed.

The script uses `config.json` for all settings, with command line arguments taking precedence:

```json
{
  "fonts": {
    "title": {
      "family": "Helvetica",
      "size": 20,
      "alignment": "center"
    },
    "file_path": {
      "family": "Helvetica", 
      "size": 16,
      "style": "bold"
    },
    "code": {
      "family": "Courier",
      "size": 13,
      "indent": 0
    }
  },
  "layout": {
    "page_size": "A4",
    "margins": {
      "top": 72,
      "bottom": 72,
      "left": 72,
      "right": 72
    }
  },
  "code_folder": "../",
  "output_folder": "output/",
  "ignore_file": "ignore.txt",
  "defaults": {
    "title": "Code Listing",
    "pages": 10,
    "filename": "code_listing.pdf",
    "update_ignore": false
  }
}
```

### Configuration Priority

1. **Command line arguments** (highest priority)
2. **User config file** (required)

**Note**: The script requires a config file. All settings must be specified in the config file.

## Output Format

The generated PDF contains complete code listings with:

1. **Title**: Centered heading with configurable font and size
2. **File Paths**: Bold headers showing relative paths from the base directory
3. **Code Blocks**: Complete source code with perfectly preserved original formatting

### Code Formatting

- **Preformatted Blocks**: Uses ReportLab's Preformatted for exact formatting preservation
- **Zero Padding**: No extra indentation added by the PDF generator
- **Original Formatting**: Preserves exact spacing and indentation from source files
- **Long Line Handling**: Automatically wraps long lines while preserving indentation
- **Monospace Font**: Uses Courier for code blocks for optimal readability
- **Relative Paths**: Shows file paths relative to the base directory

## Technical Details

### Supported File Types

The script automatically detects and processes common code and text files:
- `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.php`, `.java`, `.cpp`, `.c`, `.h`
- `.json`, `.xml`, `.yaml`, `.yml`, `.md`, `.txt`, `.sh`, `.bash`, `.sql`
- `.r`, `.rb`, `.go`, `.rs`, `.swift`, `.kt`, `.scala`, `.vue`, `.svelte`, `.pug`, `.styl`

### Code Folder

- **Default**: `../` (parent directory)
- **Configurable**: Set `code_folder` in `config.json` or use `--code-folder`
- **Recursive**: Searches all subdirectories for code files
- **Sorted**: Files are processed in alphabetical order

### Smart Page Management

The script now features intelligent page management:

- **Line Counting**: Estimates pages based on actual line count and font metrics
- **Smart Selection**: Skips files that would exceed by more than 3 pages
- **Flexible Limits**: Allows 2-3 extra pages for better utilization
- **Exact Reporting**: Uses PyPDF2 to count actual pages in generated PDF
- **Better Value**: Maximizes page utilization instead of stopping early

### Ignore File Functionality

- **Track Processed Files**: Maintains a list of already processed files
- **Skip Repeated Processing**: Automatically skips files that have been processed before
- **Wildcard Patterns**: Supports patterns like `.idea/*`, `.git/*`, `node_modules/*`, `*.log`
- **Smart Tracking**: Only saves files that were actually processed and added to the PDF

#### Ignore File Format

The ignore file supports both specific files and wildcard patterns:

```
# Files processed on 2025-08-06 12:50:30
/path/to/specific/file.py

# Optional: Add your own ignore patterns
.idea/*
.git/*
node_modules/*
*.log
```

**Supported Patterns:**
- `directory/*` - Ignore entire directories
- `*.extension` - Ignore files by extension
- `exact/path/file.py` - Ignore specific files
- `*pattern*` - Wildcard matching

## Project Structure

```
code-to-pdf/
├── generate_code_pdf.py    # Main script
├── config_sample.json      # Sample configuration file
├── config.json             # Configuration file (copy from sample)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── ignore.txt             # Track processed files (optional)
└── output/                # Generated PDFs (git-ignored)
```

## Requirements

- Python 3.6+
- reportlab>=4.0.0
- PyPDF2>=3.0.0 (for page counting)

## Troubleshooting

### File Not Found
- Ensure the `code_folder` path exists
- Check file permissions
- Verify file extensions are supported

### PDF Generation Errors
- Ensure output directory is writable
- Check available disk space
- Verify file encoding (UTF-8 recommended)

### Ignore File Issues
- Check if ignore file is readable/writable
- Use `--no-ignore` to bypass ignore file
- Use `--update-ignore` to save processed files
- Use `--ignore-file` to specify custom ignore file path

### Configuration Issues
- **Config file required**: Copy `config_sample.json` to `config.json` before running
- Use `--show-config` to see current configuration
- Check config file syntax (valid JSON)
- Verify file paths in configuration

### Page Counting Issues
- Ensure PyPDF2 is installed: `pip3 install PyPDF2`
- Check if generated PDF is readable
- Verify output directory permissions

 