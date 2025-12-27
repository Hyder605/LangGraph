from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from langgraph.types import Command, interrupt
import test_diffusion_v2
import json
import pathlib
from io import BytesIO
from agent_basev2 import build_workflow

def main():
    st.title("Manga Prompt Generator")

    config = {"configurable": {"thread_id": "manga-001"}}

    # Initialize session state for generated images
    if "generated_images" not in st.session_state:
        st.session_state["generated_images"] = {}
    if "prompts_list" not in st.session_state:
        st.session_state["prompts_list"] = []

    user_story = st.text_area("Enter your story:", height=200)

    # ---------- FIRST GENERATION ----------
    if st.button("Generate"):
        with st.spinner("Building workflow..."):
            if user_story.strip():
                workflow = build_workflow()
                st.session_state["workflow"] = workflow

                initial_state = {
                    "input_story": user_story,
                    "generation_attempts": 0,
                    "max_attempts": 5
                }
                with st.spinner("Generating story..."):
                    final_state = workflow.invoke(initial_state, config=config)

                generated_story = (
                    final_state.get("reviewed_story")
                    or final_state.get("refined_story")
                    or ""
                )

                st.session_state["edited_story"] = generated_story

                st.subheader("Generated Story")
                st.write(generated_story)

            else:
                st.warning("Please enter a story first.")

    # ---------- EDIT STORY ----------
    if "edited_story" in st.session_state:
        st.subheader("Edit the generated story:")
        edited_text = st.text_area(
            "Your edited version:",
            height=200,
            key="edited_text",
            value=st.session_state["edited_story"]
        )

        if st.button("Approve"):
            st.subheader("Your Edited Story")
            st.write(edited_text)
            st.session_state["edited_story"] = edited_text
            
            # ---------- RESUME WORKFLOW ----------
            workflow = st.session_state.get("workflow")
            if workflow:
                with st.spinner("Processing your edits..."):
                    final_after_review = workflow.invoke(
                        Command(resume=edited_text),
                        config=config
                    )

                with st.spinner("Generating prompts..."):
                    prompts = final_after_review.get('manga_image_prompts', {}).get('panel_prompts', [])
                    if prompts:
                        # Store prompts in session state
                        st.session_state["prompts_list"] = prompts
                        
                        out_dir = pathlib.Path("outputs")
                        out_dir.mkdir(exist_ok=True)
                        
                        for prompt in prompts:
                            panel_no = prompt.get('panel_number')
                            text_prompt = prompt.get('image_prompt')
                            
                            # Generate image only if not already generated
                            if panel_no not in st.session_state["generated_images"]:
                                with st.spinner(f"Generating image for panel {panel_no}..."):
                                    try:
                                        image = test_diffusion_v2.generate_image(text_prompt)
                                        st.session_state["generated_images"][panel_no] = image
                                    except Exception as e:
                                        st.error(f"Image generation failed for panel {panel_no}: {e}")
                                        continue
                    else:
                        st.warning("No extracted features found. Maybe the node did not run.")
            else:
                st.error("Workflow not initialized. Click Generate first.")

    # ---------- DISPLAY AND REGENERATE IMAGES ----------
    if st.session_state["prompts_list"]:
        st.markdown("---")
        st.header("Generated Images")
        
        for prompt in st.session_state["prompts_list"]:
            panel_no = prompt.get('panel_number')
            text_prompt = prompt.get('image_prompt')
            
            st.subheader(f"Panel {panel_no}")
            st.write(text_prompt)
            
            # Display image if it exists
            if panel_no in st.session_state["generated_images"]:
                image = st.session_state["generated_images"][panel_no]
                st.image(image, caption=f"Panel {panel_no}", use_container_width=True)
                
                # Create columns for buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download button
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    st.download_button(
                        label=f"Download Panel {panel_no}",
                        data=buffered.getvalue(),
                        file_name=f"panel_{panel_no}.png",
                        mime="image/png",
                        key=f"download_{panel_no}"
                    )
                
                with col2:
                    # Regenerate button
                    if st.button(f"Regenerate Panel {panel_no}", key=f"regen_{panel_no}"):
                        with st.spinner(f"Regenerating panel {panel_no}..."):
                            try:
                                new_image = test_diffusion_v2.generate_image(text_prompt)
                                st.session_state["generated_images"][panel_no] = new_image
                                st.success(f"Panel {panel_no} regenerated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Regeneration failed: {e}")
            
            st.markdown("---")

if __name__ == "__main__":
    main()