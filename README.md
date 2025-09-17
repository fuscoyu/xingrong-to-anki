# xingrong-to-anki

*[English](README.md) | [中文](README_zh.md)*

Convert Xingrong English lesson PDFs to Anki flashcards with automatic vocabulary extraction and unified deck generation.

## Overview

This project converts Xingrong English lesson PDFs into a single unified Anki deck with all vocabulary cards organized by lesson tags. Perfect for systematic English vocabulary learning with Chinese-English flashcards.

## Features

- 🔄 **Batch PDF Processing**: Process all lesson PDFs at once
- 🏷️ **Unified Deck with Tags**: Single deck organized by lesson tags
- 🇨🇳🇺🇸 **Chinese-English Cards**: Front (Chinese) → Back (English + phonetic)
- 📖 **Smart Content Extraction**: Automatically identifies vocabulary from page 2 onwards
- 🔍 **Duplicate Detection**: Removes duplicate vocabulary across lessons
- 🐳 **DevContainer Ready**: One-click development environment
- 🎯 **Anki Optimized**: Direct `.apkg` import with proper formatting

## Setup

### Using DevContainer (Recommended)

1. Open the project in VS Code with DevContainer extension
2. VS Code will automatically detect the `.devcontainer/devcontainer.json` and prompt to reopen in container
3. The container will automatically install dependencies from `requirements.txt`

### Manual Setup

1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Process All PDFs (Generate Unified Deck)

```bash
python main.py
```

This will:
- Process all PDF files in the `pdf/` directory
- Generate a single unified deck with all vocabulary cards
- Use tags to organize cards by lesson (e.g., `Lesson_1`, `Lesson_2`, etc.)
- Create one `.apkg` file: `星荣英语词汇大全.apkg`

### Custom Deck Name

```bash
python main.py --deck-name "My English Vocabulary"
```

### Process Single PDF

```bash
python main.py -f "零基础学英语第1课-星荣英语笔记.pdf"
```

### Custom Directories

```bash
python main.py -d my_pdfs -o my_anki_decks
```

### List Available PDFs

```bash
python main.py --list-pdfs
```

## Command Line Options

- `-f, --file`: Process a single PDF file
- `-d, --pdf-dir`: PDF directory path (default: `pdf`)
- `-o, --output-dir`: Output directory for Anki decks (default: `anki_decks`)
- `--list-pdfs`: List all PDF files and exit
- `--deck-name`: Name for the deck (default: `星荣英语词汇大全`)

## Output

The script generates a single `.apkg` file that can be imported directly into Anki:

### Unified Deck
- Creates a single deck with all vocabulary from all lessons
- Uses tags to organize cards by lesson
- File naming: `星荣英语词汇大全.apkg` (or custom name)
- Tag organization:
  - Each lesson gets a unique tag (e.g., `Lesson_1`, `Lesson_2`, `Lesson_5_5`)
  - All cards have common tags: `Xingrong`, `English`, `Vocabulary`
  - Use Anki's browser to filter by tags for studying specific lessons

## Using the Generated Decks in Anki

### Importing
1. Open Anki
2. Go to File → Import
3. Select the generated `.apkg` file
4. The unified deck will be imported with all vocabulary cards

### Studying with the Unified Deck
You can:
1. **Study all cards together**: Use the deck normally for mixed review
2. **Study specific lessons**: 
   - Open Anki's browser (Browse button)
   - Use the tag filter to select specific lessons (e.g., `Lesson_1`)
   - Create custom study sessions for specific lessons
3. **Track progress by lesson**: Use Anki's statistics to see progress per tag

## Card Format

- **Front**: Chinese text (中文)
- **Back**: English translation + phonetic pronunciation (if available)

## Project Structure

```
xingrong-to-anki/
├── .devcontainer/
│   └── devcontainer.json          # DevContainer configuration
├── pdf/                           # Input PDF files
├── anki_decks/                    # Generated Anki decks (created automatically)
├── pdf_parser.py                  # PDF content extraction
├── anki_generator.py              # Anki deck generation  
├── main.py                        # Main script
├── test_setup.py                  # Setup verification
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Development

### Testing Individual Components

```bash
# Test PDF parsing
python pdf_parser.py

# Test Anki generation
python anki_generator.py
```

### Dependencies

- `pdfplumber`: PDF text extraction
- `genanki`: Anki deck generation
- `PyPDF2`: Additional PDF processing support

## Troubleshooting

### No Cards Extracted
- Ensure PDFs contain Chinese and English text starting from page 2
- Check that the PDF is not password-protected or corrupted
- Verify the text extraction by running `python pdf_parser.py`

### Import Issues in Anki
- Ensure Anki is up to date
- Try importing one deck at a time
- Check that the `.apkg` file is not corrupted

### DevContainer Issues
- Ensure Docker is running
- Check that the DevContainer extension is installed in VS Code
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

## Contributing

1. Follow clean code principles
2. Use English comments
3. Implement proper error handling
4. Test with various PDF formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Clone your fork
3. Open in VS Code with DevContainer extension
4. Make your changes
5. Test with `python test_setup.py`
6. Submit a pull request

### Code Guidelines

- Follow clean code principles (遵循代码整洁之道)
- Use English comments (优先使用英文注释)
- Implement proper error handling (编写完善的错误处理)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Xingrong English teaching materials
- Built with [genanki](https://github.com/kerrickstaley/genanki) for Anki deck generation
- PDF processing powered by [pdfplumber](https://github.com/jsvine/pdfplumber)
