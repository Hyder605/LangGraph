from streamlit import sidebar, session_state

def display_sidebar():
    sidebar.title("Manga Generation")
    sidebar.header("Options")
    
    # User input for the story
    story_input = sidebar.text_area("Enter your story:", height=150)
    
    # Button to submit the story
    if sidebar.button("Generate Prompts"):
        if story_input:
            session_state.story = story_input
            session_state.generated_prompts = []
        else:
            sidebar.warning("Please enter a story to generate prompts.")
    
    # Display generated prompts if available
    if hasattr(session_state, 'generated_prompts') and session_state.generated_prompts:
        sidebar.header("Generated Prompts")
        for prompt in session_state.generated_prompts:
            sidebar.write(prompt)