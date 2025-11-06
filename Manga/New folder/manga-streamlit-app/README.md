# Manga Streamlit App

This project is a Streamlit application designed to generate manga image prompts based on user-provided stories. The application utilizes a pipeline that processes the input story and produces visual prompts step by step, allowing users to see the creative process unfold.

## Project Structure

```
manga-streamlit-app
├── src
│   ├── app.py                # Main entry point for the Streamlit application
│   ├── agent_basev2.py       # Core logic for generating manga prompts
│   ├── workflow_ui.py        # Manages user interface components for the workflow
│   ├── components
│   │   ├── sidebar.py        # Sidebar component for navigation and options
│   │   └── panel_view.py     # Displays generated image prompts
│   └── utils
│       └── runner.py         # Utility functions for executing the pipeline
├── .env.example               # Template for environment variables
├── .gitignore                 # Specifies files to ignore by Git
├── requirements.txt           # Lists project dependencies
└── README.md                  # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd manga-streamlit-app
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Copy the `.env.example` file to `.env` and fill in the required values.

5. **Run the application**:
   ```
   streamlit run src/app.py
   ```

## Usage Guidelines

- Open the application in your web browser.
- Input your story in the provided text box.
- Click the "Generate" button to start the manga prompt generation process.
- View the generated image prompts step by step as they are produced by the pipeline.

## Features

- User-friendly interface for story input and prompt generation.
- Step-by-step display of generated manga image prompts.
- Modular design with separate components for better maintainability.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.