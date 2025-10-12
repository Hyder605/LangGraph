#!/usr/bin/env python3
"""
Run script for the Manga Generation Streamlit App
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pydantic
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main function to run the Streamlit app"""
    
    print("🎭 AI-Powered Manga Generation System")
    print("=" * 40)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    app_file = current_dir / "src" / "app.py"
    
    if not app_file.exists():
        print("❌ Error: app.py not found in src/ directory")
        print(f"Current directory: {current_dir}")
        print("Please run this script from the manga-streamlit-app directory")
        return 1
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Set environment variables if needed
    os.environ.setdefault("STREAMLIT_THEME_BASE", "dark")
    os.environ.setdefault("STREAMLIT_THEME_PRIMARY_COLOR", "#667eea")
    
    print("🚀 Starting Streamlit app...")
    print("📱 The app will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running app: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())