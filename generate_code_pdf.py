#!/usr/bin/env python3
"""
Code to PDF Generator
Creates a PDF file with code listings from specified files.
"""

import os
import sys
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import argparse





def load_config():
    """Load configuration from config.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.json')
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file '{config_file}' not found. Please create a config.json file.")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            print(f"Loaded configuration from: {config_file}")
            return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing config file '{config_file}': {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading config file '{config_file}': {e}")





def create_styles(config):
    """Create custom styles for the PDF based on configuration."""
    styles = getSampleStyleSheet()
    
    # Get font configurations
    title_font = config['fonts']['title']
    file_path_font = config['fonts']['file_path']
    code_font = config['fonts']['code']
    
    # Title style
    if 'CustomTitle' not in styles:
        alignment = TA_CENTER if title_font.get('alignment') == 'center' else TA_LEFT
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontName=title_font['family'],
            fontSize=title_font['size'],
            alignment=alignment,
            spaceAfter=20
        ))
    
    # File path style
    if 'FilePath' not in styles:
        styles.add(ParagraphStyle(
            name='FilePath',
            parent=styles['Heading2'],
            fontName=file_path_font['family'],
            fontSize=file_path_font['size'],
            spaceAfter=10,
            spaceBefore=15
        ))
    
    # Code style - optimized for Preformatted
    if 'Code' not in styles:
        styles.add(ParagraphStyle(
            name='Code',
            fontName=code_font['family'],
            fontSize=code_font['size'],
            leading=code_font['size'] * 1.2,  # Line height
            alignment=TA_LEFT
        ))
    
    return styles


def find_code_files(folder_path, max_files=None, ignore_file=None):
    """Find code files in the specified folder."""
    code_files = []
    
    # Resolve the folder path
    if not os.path.isabs(folder_path):
        folder_path = os.path.abspath(folder_path)
    
    print(f"Looking for files in: {folder_path}")
    
    if not os.path.exists(folder_path):
        print(f"Warning: Code folder '{folder_path}' does not exist.")
        return []
    
    # Load ignored files and patterns if ignore_file is provided
    ignored_files = set()
    ignored_patterns = []
    if ignore_file and os.path.exists(ignore_file):
        try:
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Check if it's a wildcard pattern
                        if '*' in line:
                            ignored_patterns.append(line)
                        else:
                            # Convert to absolute path if it's not already
                            if not os.path.isabs(line):
                                line = os.path.abspath(os.path.join(folder_path, line))
                            ignored_files.add(line)
            print(f"Loaded {len(ignored_files)} files and {len(ignored_patterns)} patterns to ignore from {ignore_file}")
        except Exception as e:
            print(f"Error reading ignore file: {str(e)}")
    
    # Get the absolute path of this script
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Files to exclude
    excluded_files = {script_path}
    
    # Directories to exclude (including the directory containing this script)
    excluded_dirs = {script_dir}
    
    def should_ignore_file(file_path):
        """Check if a file should be ignored based on patterns and specific files."""
        # Check specific files
        if file_path in ignored_files:
            return True
            
        # Check patterns
        relative_path = os.path.relpath(file_path, folder_path)
        for pattern in ignored_patterns:
            # Convert pattern to regex-like matching
            if pattern.endswith('/*'):
                # Directory pattern
                dir_pattern = pattern[:-2]  # Remove /*
                if relative_path.startswith(dir_pattern + '/') or relative_path == dir_pattern:
                    return True
            elif pattern.startswith('*.'):
                # File extension pattern
                ext_pattern = pattern[1:]  # Remove *
                if relative_path.endswith(ext_pattern):
                    return True
            elif '*' in pattern:
                # Other wildcard patterns
                import fnmatch
                if fnmatch.fnmatch(relative_path, pattern):
                    return True
            else:
                # Exact match
                if relative_path == pattern:
                    return True
        return False
    
    # Get all files from the folder
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]
        
        for file in files:
            # Skip hidden files and common non-code files
            if not file.startswith('.') and not file.endswith(('.tmp', '.log', '.cache')):
                file_path = os.path.join(root, file)
                
                # Skip excluded files
                if file_path in excluded_files:
                    continue
                
                # Skip ignored files and patterns
                if should_ignore_file(file_path):
                    continue
                
                # Only include text files (code files)
                if is_text_file(file_path):
                    all_files.append(file_path)
    
    # Sort files by name
    all_files.sort()
    
    # Limit number of files if specified
    if max_files and len(all_files) > max_files:
        all_files = all_files[:max_files]
        print(f"Limited to {max_files} files")
    
    print(f"Found {len(all_files)} code files to process")
    return all_files


def save_processed_files(file_paths, ignore_file, max_saved_files=50):
    """Save the list of processed files to the ignore file."""
    from datetime import datetime
    try:
        # Read existing processed files to avoid duplicates
        existing_files = set()
        if os.path.exists(ignore_file):
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '*' not in line:
                        existing_files.add(line)
        
        # Filter out files that are already in the ignore file
        new_files = [f for f in file_paths if f not in existing_files]
        
        if not new_files:
            print("No new files to save to ignore file")
            return True
        
        # Append new files to the ignore file
        with open(ignore_file, 'a') as f:
            # Add timestamp comment
            f.write(f"\n# Files processed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for file_path in sorted(new_files):
                f.write(f"{file_path}\n")
        
        print(f"Saved {len(new_files)} new files to {ignore_file}")
        return True
    except Exception as e:
        print(f"Error saving to ignore file: {str(e)}")
        return False


def is_text_file(file_path):
    """Check if a file is likely a text file."""
    text_extensions = {
        '.py', '.js', '.html', '.css', '.php', '.java', '.cpp', '.c', '.h',
        '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sh', '.bash',
        '.sql', '.r', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.ts', '.jsx', '.tsx', '.vue', '.svelte', '.pug', '.styl'
    }
    
    _, ext = os.path.splitext(file_path.lower())
    return ext in text_extensions





def read_file_content(file_path):
    """Read file content and return as string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def generate_pdf(output_path, title, files_list, max_pages=None, config=None):
    """Generate PDF with code listings."""
    
    # Config is required
    if config is None:
        raise ValueError("Config parameter is required")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get page size and margins from config
    page_size = A4 if config['layout']['page_size'] == 'A4' else letter
    margins = config['layout']['margins']
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        rightMargin=margins['right'],
        leftMargin=margins['left'],
        topMargin=margins['top'],
        bottomMargin=margins['bottom']
    )
    
    # Get styles
    styles = create_styles(config)
    
    # Build story (content)
    story = []
    
    # Add title
    story.append(Paragraph(title, styles['CustomTitle']))
    story.append(Spacer(1, 20))
    
    processed_files = []  # Track files that were actually processed
    files_processed = 0
    
    # Get the base directory for relative path calculation
    base_dir = os.path.abspath(config['code_folder'])
    
    # Calculate available height per page
    page_height = page_size[1] - margins['top'] - margins['bottom']
    line_height = styles['Code'].leading
    lines_per_page = int(page_height / line_height)
    
    current_lines = 0
    estimated_pages = 1
    
    for file_item in files_list:
        # Handle both file paths (strings) and sample content (tuples)
        if isinstance(file_item, tuple):
            file_path, content = file_item
        else:
            file_path = file_item
            content = read_file_content(file_path)
            
        # Calculate relative path from base directory
        try:
            relative_path = os.path.relpath(file_path, base_dir)
        except ValueError:
            # If files are on different drives (Windows), use the full path
            relative_path = file_path
            
        # Process content to handle long lines and preserve formatting
        lines = content.split('\n')
        processed_lines = []
        
        # Calculate available width for code
        max_width = 6.0 * inch  # Available width in points
        char_width = 8  # points per character for Courier font
        max_chars = int(max_width / char_width)
        
        file_lines = 0
        for line in lines:
            if len(line) > max_chars:
                # Calculate indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Split long line
                remaining = line.lstrip()
                first_line = True
                
                while remaining:
                    if first_line:
                        # First line keeps original indentation
                        available = max_chars
                        line_part = line[:available]
                        processed_lines.append(line_part)
                        file_lines += 1
                        remaining = line[available:].lstrip()
                        first_line = False
                    else:
                        # Continuation lines get extra indent
                        continuation_indent = indent_str + '    '
                        available = max_chars - len(continuation_indent)
                        if available <= 0:
                            # If indentation is too deep, use minimal indentation
                            continuation_indent = '    '
                            available = max_chars - 4
                        
                        if available <= 0 or not remaining:
                            break
                            
                        line_part = continuation_indent + remaining[:available]
                        processed_lines.append(line_part)
                        file_lines += 1
                        remaining = remaining[available:]
            else:
                processed_lines.append(line)
                file_lines += 1
        
        # Join processed lines
        processed_content = '\n'.join(processed_lines)
        
        # Estimate if this file would exceed page limit BEFORE adding to story
        if max_pages:
            # Add estimated lines for file path heading (about 2 lines)
            estimated_total_lines = current_lines + 2 + file_lines
            estimated_pages = (estimated_total_lines // lines_per_page) + 1
            
            # Calculate how many pages we currently have
            current_pages = (current_lines // lines_per_page) + 1
            pages_remaining = max_pages - current_pages
            
            # If adding this file would exceed by more than 3 pages, skip this file and try the next one
            if estimated_pages > max_pages + 3:
                print(f"Skipping file {relative_path} - would exceed {max_pages} pages by too much (estimated {estimated_pages} pages), trying next file...")
                continue
            elif estimated_pages > max_pages:
                print(f"Including file {relative_path} - will exceed {max_pages} pages by {estimated_pages - max_pages} pages (estimated {estimated_pages} pages)")
        
        # If we get here, the file fits within the page limit
        # Add file path as heading (use relative path)
        story.append(Paragraph(relative_path, styles['FilePath']))
        
        # Update current lines count
        current_lines += 2 + file_lines
        
        # Use Preformatted for better code formatting preservation
        story.append(Preformatted(processed_content, styles['Code'], maxLineLength=max_chars))
        
        # Add this file to the processed files list
        processed_files.append(file_path)
        files_processed += 1
    
    # Build PDF
    doc.build(story)
    
    # Count actual pages by reading the generated PDF
    try:
        import PyPDF2
        with open(output_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            actual_pages = len(pdf_reader.pages)
            print(f"PDF generated successfully: {output_path}")
            print(f"Total pages generated: {actual_pages}")
            print(f"Files processed and added to PDF: {len(processed_files)}")
    except ImportError:
        # Fallback if PyPDF2 is not available
        print(f"PDF generated successfully: {output_path}")
        print(f"Files processed and added to PDF: {len(processed_files)}")
        print("Note: Install PyPDF2 to see exact page count")
    
    # Generate summary and create title.txt
    summary = generate_file_summary(processed_files, actual_pages, config)
    title_file_path = output_path.replace('.pdf', '_title.txt')
    
    try:
        with open(title_file_path, 'w', encoding='utf-8') as f:
            f.write(f"PDF: {os.path.basename(output_path)}\n")
            f.write(f"Pages: {actual_pages}\n")
            f.write(f"Files: {len(processed_files)}\n")
            f.write(f"Summary: {summary}\n")
        print(f"Title file created: {title_file_path}")
        print(f"Suggested summary: {summary}")
    except Exception as e:
        print(f"Warning: Could not create title file: {str(e)}")
    
    return processed_files


def generate_file_summary(processed_files, page_count, config=None):
    """Generate a brief summary of the PDF content based on file types and structure."""
    if not processed_files:
        return "Empty PDF. No files processed."
    
    # Check if AI summary is enabled
    ai_enabled = True
    if config and 'ai' in config:
        ai_enabled = config['ai'].get('enable_ai_summary', True)
    
    # Try AI-powered summary first if enabled
    if ai_enabled:
        ai_summary = generate_ai_summary(processed_files, page_count, config)
        if ai_summary:
            return ai_summary
    
    # Fallback to rule-based summary
    return generate_rule_based_summary(processed_files, page_count)


def generate_ai_summary(processed_files, page_count, config=None):
    """Generate AI-powered summary using Anthropic API."""
    try:
        import anthropic
        
        # Check for API key from config first, then environment variable
        api_key = None
        if config and 'ai' in config and config['ai'].get('anthropic_api_key'):
            api_key = config['ai']['anthropic_api_key']
        else:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not found in config or environment. Using rule-based summary.")
            return None
        
        # Prepare file list for AI analysis
        file_list = []
        for file_path in processed_files:
            relative_path = os.path.basename(file_path)
            _, ext = os.path.splitext(file_path.lower())
            file_list.append(f"- {relative_path} ({ext})")
        
        # Create prompt for AI
        prompt = f"""Analyze this list of code files and create a brief summary describing what was added to this PDF.

Files ({len(processed_files)} total, {page_count} pages):
{chr(10).join(file_list[:20])}{'...' if len(file_list) > 20 else ''}

Generate a summary in this format: "Added [technology/component type] [purpose/functionality]. Added new [X] pages."

Examples:
- "Added React components for user interface. Added new 15 pages."
- "Added Python backend API functions. Added new 8 pages."
- "Added CSS styling for web components. Added new 12 pages."
- "Added JavaScript utility functions. Added new 6 pages."

Focus on:
- Main technology/language used (React, Python, CSS, JavaScript, etc.)
- Component type or functionality (components, functions, styling, etc.)
- Purpose or context (UI, backend, utilities, etc.)

Respond with ONLY the summary in the specified format."""
        
        # Get AI configuration from config or use defaults
        ai_config = config.get('ai', {}) if config else {}
        model = ai_config.get('model', 'claude-3-5-sonnet-20241022')
        max_tokens = ai_config.get('max_tokens', 50)
        temperature = ai_config.get('temperature', 0.3)
        
        # Call Anthropic API
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        summary = response.content[0].text.strip()
        
        # Add page count if not included
        if str(page_count) not in summary:
            summary += f". {page_count} pages."
        
        return summary
        
    except ImportError:
        print("Warning: anthropic package not installed. Using rule-based summary.")
        return None
    except Exception as e:
        print(f"Warning: AI summary failed ({str(e)}). Using rule-based summary.")
        return None


def generate_rule_based_summary(processed_files, page_count):
    """Generate rule-based summary as fallback."""
    # Analyze file types
    file_extensions = {}
    file_types = []
    
    for file_path in processed_files:
        _, ext = os.path.splitext(file_path.lower())
        if ext:
            file_extensions[ext] = file_extensions.get(ext, 0) + 1
    
    # Determine main file types
    main_extensions = sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Map extensions to readable names
    ext_to_name = {
        '.js': 'JavaScript',
        '.jsx': 'React JSX',
        '.ts': 'TypeScript',
        '.tsx': 'React TSX',
        '.py': 'Python',
        '.html': 'HTML',
        '.css': 'CSS',
        '.styl': 'Stylus',
        '.pug': 'Pug templates',
        '.json': 'JSON config',
        '.md': 'Markdown',
        '.txt': 'Text files',
        '.sh': 'Shell scripts',
        '.sql': 'SQL queries',
        '.php': 'PHP',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'Header files',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.vue': 'Vue.js',
        '.svelte': 'Svelte'
    }
    
    # Build summary based on file types
    if len(main_extensions) == 1:
        ext, count = main_extensions[0]
        file_type = ext_to_name.get(ext, ext[1:].upper())
        if count == 1:
            summary = f"Single {file_type} file. {page_count} pages."
        else:
            summary = f"{count} {file_type} files. {page_count} pages."
    elif len(main_extensions) == 2:
        ext1, count1 = main_extensions[0]
        ext2, count2 = main_extensions[1]
        type1 = ext_to_name.get(ext1, ext1[1:].upper())
        type2 = ext_to_name.get(ext2, ext2[1:].upper())
        summary = f"{count1} {type1}, {count2} {type2}. {page_count} pages."
    else:
        # Multiple file types
        types = []
        for ext, count in main_extensions:
            file_type = ext_to_name.get(ext, ext[1:].upper())
            types.append(f"{count} {file_type}")
        summary = f"{', '.join(types)}. {page_count} pages."
    
    # Add context based on file paths
    if any('components' in f for f in processed_files):
        summary += " UI components included."
    elif any('views' in f for f in processed_files):
        summary += " Page templates included."
    elif any('gulp' in f for f in processed_files):
        summary += " Build scripts included."
    elif any('assets' in f for f in processed_files):
        summary += " Asset files included."
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='Generate PDF with code listings')
    
    # Configuration options
    parser.add_argument('--ignore-file', help='Path to ignore file (overrides config)')
    
    # Output options
    parser.add_argument('--title', help='Title for the PDF (overrides config)')
    parser.add_argument('--filename', help='Output PDF filename (overrides config)')
    parser.add_argument('--output-folder', help='Output folder path (overrides config)')
    
    # Processing options
    parser.add_argument('--pages', type=int, help='Number of pages to generate (overrides config)')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to include')
    parser.add_argument('--code-folder', help='Code folder path (overrides config)')
    
    # Control options
    parser.add_argument('--no-ignore', action='store_true', help='Process all files, ignoring the ignore file')
    parser.add_argument('--update-ignore', action='store_true', help='Update the ignore file with processed files (default: from config)')
    parser.add_argument('--show-config', action='store_true', help='Show current configuration and exit')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config()
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Override config values with command line arguments
    if args.title:
        config['defaults']['title'] = args.title
    if args.filename:
        config['defaults']['filename'] = args.filename
    if args.output_folder:
        config['output_folder'] = args.output_folder
    if args.pages:
        config['defaults']['pages'] = args.pages
    if args.code_folder:
        config['code_folder'] = args.code_folder
    if args.ignore_file:
        config['ignore_file'] = args.ignore_file
    
    # Set default update_ignore from config if not specified via command line
    if not args.update_ignore and 'update_ignore' in config['defaults']:
        args.update_ignore = config['defaults']['update_ignore']
    
    # Show configuration if requested
    if args.show_config:
        print("Current configuration:")
        print(json.dumps(config, indent=2))
        return
    
    # Ensure filename is saved in output folder
    output_folder = config['output_folder']
    filename = config['defaults']['filename']
    if not filename.startswith(output_folder):
        output_path = os.path.join(output_folder, filename)
    else:
        output_path = filename
    
    # Set up ignore file path
    ignore_file_path = config['ignore_file']
    if not os.path.isabs(ignore_file_path):
        # Make relative to script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(script_dir, ignore_file_path)
    
    # Find code files in code_folder, respecting the ignore file unless --no-ignore is specified
    if args.no_ignore:
        files_list = find_code_files(config['code_folder'], args.max_files)
        print("Ignoring the ignore file as requested")
    else:
        files_list = find_code_files(config['code_folder'], args.max_files, ignore_file_path)
    
    if not files_list:
        print("No files to process. All files may have been processed already.")
        return
    
    if args.max_files:
        print(f"Limiting to maximum {args.max_files} files")
    
    # Generate PDF and get list of files that were actually processed
    processed_files = generate_pdf(output_path, config['defaults']['title'], files_list, config['defaults']['pages'], config)
    
    # Update ignore file if requested - only save files that were actually processed
    if args.update_ignore and processed_files:
        save_processed_files(processed_files, ignore_file_path)


if __name__ == "__main__":
    main() 