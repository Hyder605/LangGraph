
### changes in version 3--------->> storing images in RAM and displaying directly without saving to disk

from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import json
import pathlib
from io import BytesIO
from agent_basev2 import build_workflow
import test_diffusion_v2

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
                out_dir = pathlib.Path("outputs")
                out_dir.mkdir(exist_ok=True)
                for prompt in prompts:
                    panel_no = prompt.get('panel_number')
                    text_prompt = prompt.get('image_prompt')
                    st.subheader(f"Panel {panel_no}")
                    st.write(text_prompt)

                    out_path = out_dir / f"panel_{panel_no}.png"
                    # call test_diffusion.generate_image for each prompt (blocking)
                    with st.spinner(f"Generating image for panel {panel_no}..."):
                        try:
                            image = test_diffusion_v2.generate_image(text_prompt)  # 👈 get in-memory image
                        except Exception as e:
                            st.error(f"Image generation failed for panel {panel_no}: {e}")
                            continue

                    # Display directly from memory
                    st.image(image, caption=f"Panel {panel_no}", use_container_width=True)

                    # Provide download button (still from memory)
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    btn = st.download_button(
                        label="Download PNG",
                        data=buffered.getvalue(),
                        file_name=f"panel_{panel_no}.png",
                        mime="image/png")
            else:
                st.write("No prompts generated. Please try again.")
        else:
            st.warning("Please enter a story to generate prompts.")

if __name__ == "__main__":
    main()