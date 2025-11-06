from streamlit import st
import json
import requests

def main():
    st.title("Manga Image Prompt Generator")
    
    # User input for the story
    user_story = st.text_area("Enter your story:", height=200)
    
    if st.button("Generate Prompts"):
        if user_story:
            # Call the pipeline to generate prompts
            with st.spinner("Generating prompts..."):
                response = requests.post("http://localhost:8000/generate", json={"input_story": user_story})
                if response.status_code == 200:
                    prompts = response.json().get("manga_image_prompts", {}).get("panel_prompts", [])
                    display_prompts(prompts)
                else:
                    st.error("Error generating prompts. Please try again.")
        else:
            st.warning("Please enter a story before generating prompts.")

def display_prompts(prompts):
    st.subheader("Generated Image Prompts:")
    for prompt in prompts:
        st.markdown(f"**Panel {prompt['panel_number']}:** {prompt['image_prompt']}")

if __name__ == "__main__":
    main()