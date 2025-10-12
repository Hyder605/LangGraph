# 🎭 AI-Powered Manga Generation System - Streamlit UI

A beautiful, interactive Streamlit web application for generating professional manga comics using AI. Transform simple stories into complete manga pages with character consistency, quality control, and iterative improvement.

## 🌟 Features

- **Interactive Story Input**: Easy-to-use interface for entering your story ideas
- **Real-time Progress Tracking**: Visual progress indicators for each generation step
- **Quality Analysis**: Automated quality scoring and improvement suggestions
- **Character Profiles**: Detailed character designs with consistency tokens
- **Panel Visualization**: Clean display of generated manga panels
- **Configurable Settings**: Adjustable quality thresholds and generation attempts
- **Export Functionality**: Save and share your generated manga

## 🎯 Key Capabilities

- ✅ **Story Refinement**: Transform raw stories into manga-style narratives
- ✅ **Character Design**: Generate detailed, consistent character profiles
- ✅ **Scene Planning**: Break stories into sequential manga scenes
- ✅ **Panel Direction**: Create professional panel-by-panel instructions
- ✅ **Quality Control**: Iterative improvement with AI-powered analysis
- ✅ **Visual Consistency**: Character tokens ensure consistency across panels

## 📁 Project Structure

```
manga-streamlit-app/
├── src/
│   ├── app.py                  # Main Streamlit application
│   ├── components/             # Reusable UI components
│   │   ├── manga_display.py    # Panel & character display components
│   │   └── progress_tracker.py # Progress tracking & workflow status
│   ├── utils/                  # Utility functions
│   │   └── state_management.py # State management & persistence
│   └── styles/
│       └── main.css           # Custom CSS styling
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── run_app.py                # Easy startup script
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (for AI generation)
- Git (for cloning)

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd manga-streamlit-app
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Using venv
   python -m venv manga_env
   
   # Windows
   manga_env\Scripts\activate
   
   # macOS/Linux  
   source manga_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

5. **Run the Application**
   
   **Option A: Using the run script (Recommended)**
   ```bash
   python run_app.py
   ```
   
   **Option B: Direct Streamlit command**
   ```bash
   streamlit run src/app.py
   ```

6. **Open Your Browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, manually navigate to the URL shown in the terminal

## 📖 Usage Guide

### Basic Workflow

1. **Enter Your Story**
   - Use the sidebar to input your story idea
   - Example: "A boy named Ibad falls in love with a girl named Aisha"

2. **Configure Settings**
   - **Max Quality Attempts**: Number of improvement iterations (1-10)
   - **Quality Threshold**: Minimum acceptable quality score (5.0-10.0)

3. **Generate Manga**
   - Click "🚀 Generate Manga" button
   - Watch real-time progress in the main area
   - Wait for completion (typically 30-60 seconds)

4. **Review Results**
   - **Final Manga Tab**: View generated panels and prompts
   - **Quality Analysis Tab**: See quality scores and improvement suggestions
   - **Generation Details Tab**: Inspect each workflow stage
   - **Raw Data Tab**: Access complete state data

### Advanced Features

#### Quality Control System
- **Automatic Analysis**: AI evaluates panel consistency and manga standards
- **Iterative Improvement**: Low-quality results trigger automatic regeneration
- **Configurable Thresholds**: Adjust quality requirements per your needs

#### Character Consistency
- **Consistency Tokens**: Unique identifiers ensure visual consistency (e.g., `IBAD_001`)
- **Detailed Profiles**: Complete character descriptions with physical traits
- **Visual References**: Optimized prompts for image generation models

#### Export & Sharing
- Copy individual panel prompts for use with image generation tools
- Export complete state data for further processing
- Save generation summaries and quality reports

## 🎯 Integration with Manga Generation Workflow

This Streamlit UI is designed to work with the main manga generation workflow located in the `../Manga/` directory. To connect it:

1. **Copy Workflow Files**
   ```bash
   # From the Manga directory, copy the workflow module
   cp ../Manga/agent_base.py ./workflow_integration.py
   ```

2. **Update Import Path**
   In `src/app.py`, uncomment and modify:
   ```python
   from workflow_integration import workflow
   ```

3. **Replace Demo Mode**
   Change `DEMO_MODE = False` in `config.py` to use the actual workflow

## 🔧 Configuration Options

Edit `config.py` to customize:

- **Quality thresholds** for different approval levels
- **UI appearance** and layout settings  
- **Workflow parameters** and model configurations
- **File paths** for outputs and temporary files
- **Demo mode** settings for testing

## 📊 Quality Metrics

The system evaluates manga quality based on:

- **Character Consistency** (25%): Same tokens and descriptions across panels
- **Visual Continuity** (20%): Consistent backgrounds and props
- **Manga Style Elements** (20%): Proper screentone, expressions, style markers
- **Story Flow** (15%): Logical narrative progression
- **Technical Quality** (10%): Proper formatting and completeness
- **Emotional Arc** (10%): Clear emotional journey across panels

- Upon launching the application, users will be prompted to enter a story idea.
- The application will process the input and guide users through the manga generation workflow.
- Users can track the progress of the generation and view the resulting manga panels.

## Features

- **Story Refinement**: The app refines user input into a concise manga-style story.
- **Feature Extraction**: Key features of the story are extracted for character and scene development.
- **Character Design**: Generates detailed character profiles for consistent drawing.
- **Scene and Panel Generation**: Breaks the story into scenes and generates manga panels.
- **Progress Tracking**: Visual indicators to show the current status of the manga generation workflow.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.