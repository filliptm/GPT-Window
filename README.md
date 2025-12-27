# GPT-Window

A professional desktop application for analyzing screenshots using OpenAI's GPT Vision API, with built-in video processing tools.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img width="1302" alt="Screenshot 2025-02-11 at 6 45 09 PM" src="https://github.com/user-attachments/assets/3ed0a9ae-4914-48c6-a32f-02787c851ea5" />

## Features

### GPT Vision Desktop Application
- **Transparent Overlay Window**: Draggable and resizable window for selecting screen regions
- **Real-time Screenshot Analysis**: Capture and analyze screen content with GPT Vision API
- **Secure API Key Management**: Environment variable support with input validation
- **Comprehensive Error Handling**: Detailed error messages and logging

### Video Processing Tools
- **PNG to MP4 Compiler**: Convert PNG image sequences to MP4 videos
- **Video Looper**: Loop videos a specified number of times
- **Video Processor**: Resize videos and limit frame counts

## Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Install from Source

```bash
# Clone the repository
git clone https://github.com/filliptm/GPT-Window.git
cd GPT-Window

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Usage

### Setting Up Your API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

Or create a `.env` file in the project directory:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### Running the GPT Vision Application

```bash
# Using the installed command
gpt-window

# Or using Python module
python -m gpt_window
```

#### How to Use:
1. The application will launch with a red transparent window overlay
2. Drag and resize the overlay to select the screen region you want to analyze
3. Enter your OpenAI API key in the control panel (if not set via environment)
4. Type your query in the input box (e.g., "What's in this image?")
5. Click "Send" to analyze the screenshot

### Video Processing Tools

#### PNG to MP4 Compiler

Convert sequences of PNG files to MP4 videos:

```bash
# Process subdirectories in the default input folder
gpt-video-compile

# Specify a custom input directory
gpt-video-compile /path/to/png/folders

# Custom output directory and FPS
gpt-video-compile /path/to/png/folders --output_dir ./videos --fps 24

# Process recursively (including main directory)
gpt-video-compile --recursive
```

**Expected PNG naming**: `base_name_0001.png`, `base_name_0002.png`, etc.

#### Video Looper

Loop videos a specified number of times:

```bash
# Loop all videos in default folder 3 times
gpt-video-loop

# Custom folder and loop count
gpt-video-loop /path/to/videos --loop_count 5

# Process recursively
gpt-video-loop --recursive
```

#### Video Processor

Resize videos and limit frame count:

```bash
# Process videos with default settings (1280px max, 100 frames max)
gpt-video-process

# Custom directory and settings
gpt-video-process /path/to/videos --max_dimension 720 --max_frames 50
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | (required) |
| `GPT_WINDOW_INPUT_DIR` | Input directory for video tools | `./input` |
| `GPT_WINDOW_OUTPUT_DIR` | Output directory for video tools | `./output` |
| `GPT_WINDOW_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `GPT_WINDOW_LOG_FILE` | Path to log file (optional) | None |

### Application Settings

Configure settings programmatically:

```python
from gpt_window.config.settings import Settings

settings = Settings(
    openai_api_key="sk-...",
    openai_model="gpt-4o-mini",
    video_fps=24,
    target_size=1024
)
```

## Development

### Setting Up Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=gpt_window --cov-report=html

# Format code
black gpt_window tests
isort gpt_window tests

# Type checking
mypy gpt_window

# Linting
flake8 gpt_window tests
```

### Project Structure

```
gpt_window/
├── config/          # Configuration and settings
│   ├── settings.py
│   ├── constants.py
│   └── logging_config.py
├── core/            # Core functionality
│   ├── api/         # API handlers
│   ├── utils/       # Utilities (screenshot, validators)
│   └── exceptions.py
├── ui/              # User interface components
│   ├── main_window.py
│   ├── control_panel.py
│   └── transparent_window.py
└── video_tools/     # Video processing utilities
    ├── compiler.py
    ├── looper.py
    └── processor.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=gpt_window --cov-report=html
open htmlcov/index.html
```

## Architecture

### Key Components

1. **TransparentWindow**: Frameless Qt window for screen region selection
2. **ControlPanel**: UI for API key input, queries, and response display
3. **OpenAIHandler**: API client with retry logic and rate limiting
4. **Video Tools**: Standalone utilities for video processing

### Error Handling

The application uses custom exception classes for different error types:

- `APIKeyError`: API key validation failures
- `APIResponseError`: API request/response errors
- `ScreenshotError`: Screenshot capture failures
- `VideoProcessingError`: Video processing failures
- `ValidationError`: Input validation failures

### Logging

Structured logging is available throughout the application:

```python
from gpt_window.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.error("An error occurred", exc_info=True)
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **API key is cleared from memory** when the application closes
3. **Input validation** on all user inputs
4. **Secure file operations** with proper error handling
5. **Sandboxed temporary files** for video processing

## Troubleshooting

### Common Issues

**"API key is not set" error**:
- Set the `OPENAI_API_KEY` environment variable
- Or enter your API key in the control panel

**Screenshot appears blank**:
- Ensure the overlay window is positioned over visible content
- Check that screen recording permissions are granted (macOS)

**Video processing fails**:
- Verify input files exist and are readable
- Check available disk space
- Review logs for detailed error messages

**Import errors after installation**:
- Ensure you're using Python 3.10+
- Reinstall dependencies: `pip install -e .`

### Getting Help

For bugs and feature requests, please [open an issue](https://github.com/filliptm/GPT-Window/issues).

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Powered by [OpenAI GPT-4](https://openai.com/gpt-4)
- Video processing with [MoviePy](https://zulko.github.io/moviepy/) and [OpenCV](https://opencv.org/)

## Changelog

### Version 1.0.0 (2025)

#### New Features
- Complete rewrite with modern Python best practices
- Type hints throughout the codebase
- Comprehensive error handling and logging
- Test suite with pytest
- Structured package architecture
- CLI tools for video processing

#### Security
- Improved API key handling
- Input validation on all user inputs
- Secure temporary file handling

#### Developer Experience
- Configured with pyproject.toml
- Black/isort code formatting
- mypy type checking
- GitHub Actions CI/CD ready
- Comprehensive documentation

---

**Made with ❤️ using Python and OpenAI**
