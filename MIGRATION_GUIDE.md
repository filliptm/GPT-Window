# Migration Guide: GPT-Window v1.0.0

This guide explains the changes made during the comprehensive refactoring of GPT-Window and how to migrate from the old code structure.

## Summary of Changes

The project has been completely refactored with modern Python best practices, improved security, comprehensive error handling, and a modular architecture.

## Old vs New Structure

### Old Structure (Flat)
```
GPT-Window/
├── main.py
├── gui.py
├── api_handler.py
├── utils.py
├── compile video.py
├── loop videos.py
├── process_videos.py
└── requirements.txt
```

### New Structure (Modular)
```
GPT-Window/
├── gpt_window/              # Main package
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── config/              # Configuration
│   ├── core/                # Core functionality
│   │   ├── api/             # API handlers
│   │   ├── utils/           # Utilities
│   │   └── exceptions.py    # Custom exceptions
│   ├── ui/                  # UI components
│   └── video_tools/         # Video processing
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD
├── pyproject.toml           # Modern config
├── requirements.txt         # Updated deps
└── README.md               # Comprehensive docs
```

## File Migration Map

| Old File | New Location | Changes |
|----------|--------------|---------|
| `main.py` | `gpt_window/__main__.py` | Added logging setup, settings loading |
| `gui.py` | Split into 3 files: | Better separation of concerns |
| - TransparentWindow | `gpt_window/ui/transparent_window.py` | Type hints, improved docstrings |
| - ControlPanel | `gpt_window/ui/control_panel.py` | Better error handling, security |
| - MainWindow | `gpt_window/ui/main_window.py` | Cleaner lifecycle management |
| `api_handler.py` | `gpt_window/core/api/openai_handler.py` | Retry logic, validation, logging |
| `utils.py` | `gpt_window/core/utils/screenshot.py` | Proper error handling, validation |
| `compile video.py` | `gpt_window/video_tools/compiler.py` | Type hints, better error handling |
| `loop videos.py` | `gpt_window/video_tools/looper.py` | Safe file operations, validation |
| `process_videos.py` | `gpt_window/video_tools/processor.py` | Improved resource management |

## Key Changes

### 1. Installation & Setup

**Old:**
```bash
python main.py
```

**New:**
```bash
# Install as package
pip install -e .

# Run application
gpt-window
# or
python -m gpt_window

# Run video tools
gpt-video-compile
gpt-video-loop
gpt-video-process
```

### 2. API Key Management

**Old:**
- API key entered in GUI only
- Displayed in plain text
- Stored in memory without validation

**New:**
- Environment variable support (`OPENAI_API_KEY`)
- Input validation with proper error messages
- Secure handling (cleared from memory)
- API key hidden after setting

```bash
# Set via environment
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Configuration

**Old:**
- Hardcoded paths in each file
- No centralized configuration

**New:**
- Centralized settings in `gpt_window/config/settings.py`
- Environment variable support
- Type-safe configuration with dataclasses

```python
from gpt_window.config.settings import Settings

settings = Settings.from_env()
```

**Environment Variables:**
```bash
export GPT_WINDOW_INPUT_DIR="/path/to/input"
export GPT_WINDOW_OUTPUT_DIR="/path/to/output"
export GPT_WINDOW_LOG_LEVEL="DEBUG"
```

### 4. Error Handling

**Old:**
```python
except Exception as e:
    print(f"Error: {e}")
```

**New:**
```python
from gpt_window.core.exceptions import APIKeyError, ScreenshotError

try:
    result = api_handler.send_request(image, query)
except APIKeyError as e:
    logger.error(f"API key error: {e}")
    # Handle appropriately
except ScreenshotError as e:
    logger.error(f"Screenshot error: {e}")
    # Handle appropriately
```

### 5. Logging

**Old:**
- Simple print() statements
- No log levels
- No persistent logs

**New:**
- Structured logging throughout
- Configurable log levels
- Optional file logging

```python
from gpt_window.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Starting operation")
logger.error("Error occurred", exc_info=True)
```

### 6. Type Hints

**Old:**
```python
def capture_screenshot(geometry):
    ...
```

**New:**
```python
from typing import Optional
from PIL import Image
from PyQt5.QtCore import QRect

def capture_screenshot(geometry: QRect) -> Optional[Image.Image]:
    """
    Capture a screenshot of the specified screen region.

    Args:
        geometry: QRect defining the screen region.

    Returns:
        PIL Image or None if capture fails.
    """
    ...
```

### 7. Video Tools

**Old:**
- Hardcoded paths
- Bare except clauses
- No validation

**New:**
- Command-line arguments
- Environment variable support
- Proper error handling
- Input validation

**Old:**
```python
# compile video.py
DEFAULT_INPUT_DIR = "/Users/fillipisgro/Downloads/..."
```

**New:**
```bash
# Use defaults from environment
gpt-video-compile

# Or specify paths
gpt-video-compile /path/to/input --output_dir /path/to/output --fps 24
```

## Breaking Changes

### 1. Import Paths

**Old:**
```python
from gui import TransparentWindow
from api_handler import APIHandler
from utils import capture_screenshot
```

**New:**
```python
from gpt_window.ui import TransparentWindow
from gpt_window.core.api import OpenAIHandler
from gpt_window.core.utils import capture_screenshot
```

### 2. Class Names

- `APIHandler` → `OpenAIHandler` (more descriptive)

### 3. Function Signatures

Most functions now have type hints and may raise specific exceptions instead of returning error strings.

**Old:**
```python
def send_request(self, image, query):
    try:
        # ...
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"
```

**New:**
```python
def send_request(self, image: Image.Image, query: str) -> str:
    """
    Send API request.

    Raises:
        APIKeyError: If API key not set
        APIResponseError: If API request fails
    """
    # ... implementation
```

### 4. Video Tool Scripts

**Old:**
```bash
python "compile video.py"
python "loop videos.py"
python process_videos.py
```

**New:**
```bash
gpt-video-compile
gpt-video-loop
gpt-video-process
```

## Migration Steps

### For End Users

1. **Uninstall old dependencies (optional):**
   ```bash
   pip uninstall aiohttp pyinstaller
   ```

2. **Install new package:**
   ```bash
   pip install -e .
   ```

3. **Set up environment:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

4. **Run application:**
   ```bash
   gpt-window
   ```

### For Developers

1. **Update imports in your code:**
   ```python
   # Old
   from api_handler import APIHandler

   # New
   from gpt_window.core.api import OpenAIHandler
   ```

2. **Handle specific exceptions:**
   ```python
   from gpt_window.core.exceptions import (
       APIKeyError,
       APIResponseError,
       ScreenshotError
   )
   ```

3. **Use logging instead of print:**
   ```python
   from gpt_window.config.logging_config import get_logger

   logger = get_logger(__name__)
   logger.info("Message")
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## New Features

### 1. Comprehensive Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gpt_window --cov-report=html

# Run specific tests
pytest tests/test_validators.py -v
```

### 2. Code Quality Tools

```bash
# Format code
black gpt_window tests
isort gpt_window tests

# Type checking
mypy gpt_window

# Linting
flake8 gpt_window tests
```

### 3. CI/CD

GitHub Actions workflow automatically:
- Runs tests on multiple OS (Linux, macOS, Windows)
- Tests Python 3.10, 3.11, 3.12
- Checks code formatting
- Runs type checking
- Generates coverage reports

### 4. Input Validation

All user inputs are now validated:

```python
from gpt_window.core.utils.validators import (
    validate_api_key,
    validate_fps,
    validate_directory,
    sanitize_filename
)

# Raises ValidationError if invalid
fps = validate_fps(user_input)
```

### 5. Retry Logic

API calls now have automatic retry with exponential backoff:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def send_request(self, image, query):
    # Automatically retries on rate limit or API errors
    ...
```

## Troubleshooting Migration

### "Module not found" errors

Make sure you've installed the package:
```bash
pip install -e .
```

### "API key not found" errors

Set the environment variable:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Video tools can't find files

The video tools now use environment variables for paths:
```bash
export GPT_WINDOW_INPUT_DIR="/path/to/your/files"
gpt-video-compile
```

Or pass paths as arguments:
```bash
gpt-video-compile /path/to/input --output_dir /path/to/output
```

### Tests fail on import

Make sure all dependencies are installed:
```bash
pip install -e ".[dev]"
```

## Support

If you encounter issues during migration:

1. Check the [README.md](README.md) for updated usage instructions
2. Review the comprehensive implementation plan at `.automaker/IMPLEMENTATION_PLAN.md`
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version)

## Benefits of New Architecture

✅ **Type Safety**: Full type hints for better IDE support and fewer bugs

✅ **Error Handling**: Specific exception classes for different error types

✅ **Logging**: Structured logging with configurable levels

✅ **Testing**: Comprehensive test suite with >80% coverage target

✅ **Security**: Proper API key validation and secure handling

✅ **Maintainability**: Modular architecture, clear separation of concerns

✅ **Documentation**: Comprehensive docstrings and README

✅ **CI/CD**: Automated testing on multiple platforms

✅ **Code Quality**: Black, isort, mypy, flake8 configured

✅ **Flexibility**: Environment variables and CLI arguments for configuration
