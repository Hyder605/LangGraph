import streamlit as st
import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path to import the manga generation workflow
parent_dir = Path(__file__).parent.parent.parent / "Manga"
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from components.manga_display import display_manga_panels, display_character_profiles, display_scene_breakdown
from components.progress_tracker import ProgressTracker
from utils.state_management import StateManager

# Global variables for workflow state
DEMO_MODE = True
WORKFLOW_ERROR = None
generate_manga = None

def load_workflow():
    """Try to load the manga generation workflow"""
    global DEMO_MODE, WORKFLOW_ERROR, generate_manga
    
    try:
        import sys
        parent_dir = Path(__file__).parent.parent.parent / "Manga"
        sys.path.append(str(parent_dir))
        from manga_workflow import generate_manga as _generate_manga
        generate_manga = _generate_manga
        DEMO_MODE = False
        return "✅ Manga generation workflow loaded successfully!"
    except ImportError as e:
        DEMO_MODE = True
        WORKFLOW_ERROR = f"Import error: {e}"
        return f"⚠️ Manga generation workflow not imported: {e}. Using demo mode."
    except Exception as e:
        DEMO_MODE = True  
        WORKFLOW_ERROR = f"Workflow error: {e}"
        return f"⚠️ Workflow initialization failed: {e}. Using demo mode."

def main():
    # Page config
    st.set_page_config(
        page_title="AI Manga Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Try to load workflow and show status
    workflow_status = load_workflow()
    if "✅" in workflow_status:
        st.success(workflow_status)
    else:
        st.warning(workflow_status)
    
    # Main title
    st.title("🎭 AI-Powered Manga Generation System")
    st.markdown("Transform your stories into professional manga comics using AI")
    
    # Initialize session state
    if 'state_manager' not in st.session_state:
        st.session_state.state_manager = StateManager()
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False
    
    state_manager = st.session_state.state_manager
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📝 Story Input")
        
        # Story input
        input_story = st.text_area(
            "Enter your story:",
            height=150,
            placeholder="e.g., A boy named Ibad falls in love with a girl named Aisha...",
            help="Write a simple story that will be transformed into manga"
        )
        
        # Configuration
        st.header("⚙️ Generation Settings")
        
        # Mode information
        if DEMO_MODE:
            st.info("🎬 **Demo Mode Active**")
            if WORKFLOW_ERROR:
                st.error(f"Workflow Error: {WORKFLOW_ERROR}")
            st.markdown("""
            **Note:** The real AI workflow requires:
            - Valid Google Gemini API key
            - Available API quota (50 requests/day on free tier)
            
            Demo mode shows sample output structure.
            """)
        else:
            st.success("🤖 **AI Workflow Ready**")
            st.info("⚠️ **Quota Warning:** If you see quota errors, you've reached the daily limit (50 requests). The app will automatically fall back to demo mode.")
        
        max_attempts = st.number_input(
            "Max Quality Attempts:",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of times the system will try to improve quality"
        )
        
        quality_threshold = st.slider(
            "Quality Threshold:",
            min_value=5.0,
            max_value=10.0,
            value=7.5,
            step=0.1,
            help="Minimum quality score to accept (higher = better quality)"
        )
        
        # Generate button
        generate_clicked = st.button(
            "🚀 Generate Manga",
            type="primary",
            use_container_width=True
        )
        
        # Clear button
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.state_manager = StateManager()
            st.session_state.generation_complete = False
            st.rerun()
    
    # Main content area
    if generate_clicked and input_story.strip():
        generate_manga_ui(input_story, max_attempts, quality_threshold, state_manager)
    elif generate_clicked:
        st.error("Please enter a story first!")
    
    # Display results if available
    if st.session_state.generation_complete:
        display_results(state_manager.get_state())

def generate_manga_ui(input_story, max_attempts, quality_threshold, state_manager):
    """Generate manga using the workflow"""
    
    # Update state with input parameters
    state_manager.update_state('input_story', input_story)
    state_manager.update_state('max_attempts', max_attempts)
    state_manager.update_state('generation_attempts', 0)
    
    # Progress container
    with st.container():
        st.header("🔄 Generation Progress")
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker()
        progress_container = st.empty()
        
        try:
            with st.spinner("Generating your manga..."):
                if not DEMO_MODE:
                    try:
                        # Use real workflow
                        final_state = generate_manga(input_story, max_attempts)
                        
                        # Check if there was an error in the workflow
                        if 'error' in final_state:
                            raise Exception(f"Workflow error: {final_state['error']}")
                        
                        # Update state manager with results
                        for key, value in final_state.items():
                            state_manager.update_state(key, value)
                        
                        st.success("✅ Manga generation completed with real AI workflow!")
                        
                    except Exception as workflow_error:
                        st.warning(f"⚠️ AI workflow failed: {str(workflow_error)}")
                        st.info("🎬 Switching to demo mode for this generation...")
                        
                        # Fall back to demo mode
                        demo_state = create_demo_state(input_story, max_attempts)
                        for key, value in demo_state.items():
                            state_manager.update_state(key, value)
                        
                        st.success("✅ Manga generation completed with demo data!")
                else:
                    # Demo data mode
                    st.info("🎬 Running in demo mode (AI workflow not available)")
                    demo_state = create_demo_state(input_story, max_attempts)
                    
                    # Update state manager with results  
                    for key, value in demo_state.items():
                        state_manager.update_state(key, value)
                    
                    st.success("✅ Manga generation completed with demo data!")
                
                st.session_state.generation_complete = True
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Critical error during generation: {str(e)}")
            st.exception(e)

def create_demo_state(input_story, max_attempts):
    """Create demo state for testing UI (replace with actual workflow)"""
    return {
        'refined_story': f"Refined version: {input_story} [With manga-style sound effects: POW! THUD!]",
        'extracted_features': {
            'main_characters': ['Ibad', 'Aisha'],
            'setting': 'School courtyard',
            'mood_and_tone': ['romantic', 'comedic'],
            'conflict_or_goal': 'Boy trying to confess love'
        },
        'character_feature': {
            'characters': [{
                'name_or_role': 'Shy Boy',
                'canonical_name': 'Ibad',
                'consistency_token': 'IBAD_001',
                'hair': 'messy black hair',
                'eyes': 'large brown eyes',
                'clothing': 'school uniform'
            }]
        },
        'manga_image_prompts': {
            'page_number': 1,
            'panel_prompts': [
                {
                    'panel_number': 1,
                    'image_prompt': 'Wide shot school courtyard, IBAD_001 teenage boy messy hair, spotting girl, cherry blossoms, in consistent manga style'
                },
                {
                    'panel_number': 2,
                    'image_prompt': 'Close-up IBAD_001 nervous expression, heart beating, POW sound effect, in consistent manga style'
                }
            ]
        },
        'prompt_analysis': {
            'overall_score': 8.2,
            'total_panels': 2,
            'generation_attempt': 1,
            'needs_regeneration': False
        }
    }

def display_results(state):
    """Display the generated manga results"""
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Final Manga", 
        "📊 Quality Analysis", 
        "🔍 Generation Details",
        "📋 Raw Data"
    ])
    
    with tab1:
        st.header("Generated Manga Panels")
        display_manga_panels(state.get("manga_image_prompts", {}))
    
    with tab2:
        st.header("Quality Analysis")
        display_quality_analysis(state.get("prompt_analysis", {}))
    
    with tab3:
        st.header("Generation Process")
        display_generation_details(state)
    
    with tab4:
        st.header("Raw State Data")
        display_raw_data(state)

def display_quality_analysis(analysis):
    """Display quality analysis results"""
    
    if not analysis:
        st.warning("No quality analysis available")
        return
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{analysis.get('overall_score', 0):.1f}/10"
        )
    
    with col2:
        st.metric(
            "Total Panels",
            analysis.get('total_panels', 0)
        )
    
    with col3:
        st.metric(
            "Generation Attempts",
            analysis.get('generation_attempt', 0)
        )
    
    with col4:
        needs_improvement = analysis.get('panels_needing_improvement', 0)
        st.metric(
            "Panels Needing Work",
            needs_improvement
        )

def display_generation_details(state):
    """Display detailed generation process information"""
    
    stages = [
        ("Story Refinement", "refined_story"),
        ("Feature Extraction", "extracted_features"),
        ("Character Design", "character_feature"),
        ("Scene Planning", "scene_features"),
        ("Panel Direction", "panel_scenes"),
        ("Image Prompts", "manga_image_prompts")
    ]
    
    for stage_name, state_key in stages:
        with st.expander(f"📋 {stage_name}"):
            data = state.get(state_key)
            if data:
                if isinstance(data, str):
                    st.text_area("Output:", data, height=100, disabled=True)
                else:
                    st.json(data)
            else:
                st.warning(f"No data available for {stage_name}")

def display_raw_data(state):
    """Display raw state data"""
    
    if st.checkbox("Show full state data"):
        st.json(state)
    else:
        st.info("Check the box above to view complete raw data")

def load_css():
    """Load custom CSS styling"""
    
    css_path = Path(__file__).parent / "styles" / "main.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Default styling if CSS file doesn't exist
        st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main-header {
            color: #2e4057;
            text-align: center;
            padding: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

def run_manga_generation(state):
    """Call the actual manga generation workflow"""
    # This should call your actual workflow
    # return workflow.invoke(state)
    return state

if __name__ == "__main__":
    main()