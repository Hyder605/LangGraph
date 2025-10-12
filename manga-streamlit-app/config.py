# Configuration settings for the manga comic generation application
import os
from pathlib import Path

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDqjOMA44U8w7FNtEFUHLKImRbX7lYyGZI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_key_here")  # If using OpenAI

# Application Settings
APP_TITLE = "AI-Powered Manga Generation System"
APP_ICON = "📚"
PAGE_LAYOUT = "wide"

# Default Generation Settings
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_QUALITY_THRESHOLD = 7.5
DEFAULT_GENERATION_ATTEMPTS = 0
MAX_PROBLEMATIC_PANELS = 1

# Workflow Configuration
WORKFLOW_STEPS = [
    "Story Refinement",
    "Feature Extraction", 
    "Character Design",
    "Scene Planning",
    "Panel Direction",
    "Prompt Generation",
    "Quality Analysis"
]

# Quality Thresholds
QUALITY_THRESHOLDS = {
    "EXCELLENT": 9.0,
    "GOOD": 7.5,
    "ACCEPTABLE": 6.0,
    "NEEDS_IMPROVEMENT": 4.0
}

# File Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
for directory in [OUTPUT_DIR, IMAGES_DIR, DATA_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# UI Configuration
SIDEBAR_WIDTH = 300
MAIN_CONTAINER_WIDTH = 800
PANEL_DISPLAY_COLUMNS = 2

# Manga Generation Parameters
MAX_PANELS_PER_PAGE = 6
MIN_PANELS_PER_PAGE = 3
DEFAULT_PANELS_PER_PAGE = 4

# Character Consistency
CHARACTER_TOKEN_PREFIX = "CHAR_"
MAX_CHARACTERS_PER_STORY = 10

# Model Configuration
DEFAULT_MODEL = "gemini-2.0-flash-exp"
FALLBACK_MODEL = "gemini-1.5-flash"
MAX_TOKENS_PER_REQUEST = 4000

# Demo Mode (when actual workflow is not available)
DEMO_MODE = True
DEMO_DELAY = 0.5  # seconds between demo steps

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "manga_app.log"

# Session State Keys
SESSION_KEYS = {
    "STATE_MANAGER": "state_manager",
    "GENERATION_COMPLETE": "generation_complete",
    "CURRENT_WORKFLOW": "current_workflow",
    "USER_PREFERENCES": "user_preferences"
}