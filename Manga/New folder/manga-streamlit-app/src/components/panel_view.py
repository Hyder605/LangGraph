from typing import List, Dict
import streamlit as st

def display_panel_prompts(prompts: List[Dict]) -> None:
    st.header("Generated Image Prompts")
    
    for prompt in prompts:
        st.subheader(f"Panel {prompt['panel_number']}")
        st.write(prompt['image_prompt'])
        st.markdown("---")  # Add a horizontal line for separation

# This file is responsible for displaying the generated image prompts in a visually appealing manner.