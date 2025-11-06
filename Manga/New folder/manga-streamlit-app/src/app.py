from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import json
from agent_basev2 import build_workflow

def main():
    st.title("Manga Prompt Generator")
    
    # User input for the story
    user_story = st.text_area("Enter your story:", height=200)
    
    if st.button("Generate Prompts"):
        if user_story:
            # Initialize the workflow
            workflow = build_workflow()
            initial_state = {
                'input_story': user_story,
                'generation_attempts': 0,
                'max_attempts': 5
            }
            
            # Invoke the workflow
            final_state = workflow.invoke(initial_state)
            
            # Display the generated image prompts step by step
            prompts = final_state.get('manga_image_prompts', {}).get('panel_prompts', [])
            if prompts:
                for prompt in prompts:
                    st.subheader(f"Panel {prompt['panel_number']}")
                    st.write(prompt['image_prompt'])
            else:
                st.write("No prompts generated. Please try again.")
        else:
            st.warning("Please enter a story to generate prompts.")

if __name__ == "__main__":
    main()