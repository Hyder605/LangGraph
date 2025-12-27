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

                #     # ---------- DISPLAY FEATURES ----------
                # with st.spinner("Extracting features..."):    
                #     if "extracted_features" in final_after_review:
                #         features = final_after_review["extracted_features"]

                #         st.subheader("Extracted Features")

                #         st.write("### Features")
                #         st.write(features)

                with st.spinner("Generating prompts..."):
                    # ---------- Prompts ----------
                    # if "manga_image_prompts" in final_after_review:
                    #     manga_image_prompts = final_after_review["manga_image_prompts"]

                    #     st.subheader("manga_image_prompts")

                    #     st.write("### manga_image_promptss")
                    #     st.write(manga_image_prompts)

                        prompts = final_after_review.get('manga_image_prompts', {}).get('panel_prompts', [])
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
                                st.image(image, caption=f"Panel {panel_no}", width=True)

                                # Provide download button (still from memory)
                                buffered = BytesIO()
                                image.save(buffered, format="PNG")
                                btn = st.download_button(
                                    label="Download PNG",
                                    data=buffered.getvalue(),
                                    file_name=f"panel_{panel_no}.png",
                                    mime="image/png")


                        else:
                            st.warning("No extracted features found. Maybe the node did not run.")
            else:
                st.error("Workflow not initialized. Click Generate first.")


            # # Display the generated image prompts step by step
            # prompts = final_state.get('manga_image_prompts', {}).get('panel_prompts', [])
            # if prompts:
            #     for prompt in prompts:
            #         st.subheader(f"Panel {prompt['panel_number']}")
            #         st.write(prompt['image_prompt'])
            # else:
            #     st.write("No prompts generated. Please try again.")
    else:
            st.warning("Please enter a story to generate prompts.")

if __name__ == "__main__":
    main()


