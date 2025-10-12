import streamlit as st
import json

def display_manga_panels(manga_prompts):
    """Display manga panels in a comic-style layout"""
    
    if not manga_prompts:
        st.warning("No manga panels generated yet.")
        return
    
    panel_prompts = manga_prompts.get("panel_prompts", [])
    page_number = manga_prompts.get("page_number", 1)
    
    if not panel_prompts:
        st.warning("No panel prompts found.")
        return
    
    st.subheader(f"📖 Manga Page {page_number}")
    st.markdown(f"*Generated {len(panel_prompts)} panels*")
    
    # Display panels in a grid layout
    for i, panel in enumerate(panel_prompts):
        panel_number = panel.get("panel_number", i + 1)
        image_prompt = panel.get("image_prompt", "")
        
        # Create a styled panel container
        with st.container():
            st.markdown(f"""
            <div style="
                border: 2px solid #333;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="margin-top: 0; color: #333;">🎬 Panel {panel_number}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Display the image prompt
            st.text_area(
                f"Image Generation Prompt:",
                image_prompt,
                height=120,
                disabled=True,
                key=f"panel_{panel_number}_prompt"
            )
            
            # Add a placeholder for actual image (when integrated with image generation)
            st.info("🎨 Image will be generated here when connected to image generation API")
            
            # Add copy button for the prompt
            if st.button(f"📋 Copy Prompt", key=f"copy_{panel_number}"):
                st.code(image_prompt)
                st.success("Prompt displayed above for easy copying!")
            
            st.markdown("---")

def display_character_profiles(characters):
    """Display character profiles in a nice format"""
    
    if not characters or not characters.get("characters"):
        st.warning("No character profiles available.")
        return
    
    st.subheader("👥 Character Profiles")
    
    char_list = characters.get("characters", [])
    
    # Create columns for character display
    cols = st.columns(min(len(char_list), 3))
    
    for i, character in enumerate(char_list):
        col_idx = i % 3
        
        with cols[col_idx]:
            with st.expander(f"Character: {character.get('name_or_role', 'Unknown')}"):
                
                # Basic info
                st.write(f"**Name:** {character.get('canonical_name', 'N/A')}")
                st.write(f"**Role:** {character.get('name_or_role', 'N/A')}")
                st.write(f"**Age:** {character.get('age_range', 'N/A')}")
                
                # Physical description
                st.write("**Physical Description:**")
                st.write(f"- Hair: {character.get('hair', 'N/A')}")
                st.write(f"- Eyes: {character.get('eyes', 'N/A')}")
                st.write(f"- Body: {character.get('body_type', 'N/A')}")
                
                # Clothing and style
                st.write(f"**Clothing:** {character.get('clothing', 'N/A')}")
                
                # Consistency token (important for image generation)
                token = character.get('consistency_token', 'N/A')
                st.code(f"Consistency Token: {token}")
                
                # Visual reference
                ref_prompt = character.get('visual_reference_prompt', 'N/A')
                if ref_prompt != 'N/A':
                    st.write("**Visual Reference:**")
                    st.text_area("", ref_prompt, height=60, disabled=True, key=f"char_ref_{i}")

def display_scene_breakdown(scenes):
    """Display scene breakdown information"""
    
    if not scenes or not scenes.get("scenes"):
        st.warning("No scene information available.")
        return
    
    st.subheader("🎬 Scene Breakdown")
    
    scene_list = scenes.get("scenes", [])
    
    for scene in scene_list:
        scene_num = scene.get("scene_number", "?")
        summary = scene.get("summary", "No summary available")
        
        with st.expander(f"Scene {scene_num}: {summary[:50]}..."):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Setting:**")
                st.write(scene.get("setting_details", "N/A"))
                
                st.write("**Characters:**")
                characters = scene.get("characters_involved", [])
                for char in characters:
                    st.write(f"- {char}")
            
            with col2:
                st.write("**Actions:**")
                actions = scene.get("actions", [])
                for action in actions:
                    st.write(f"• {action}")
                
                st.write("**Emotions:**")
                emotions = scene.get("emotions", [])
                for emotion in emotions:
                    st.write(f"💭 {emotion}")
            
            # Sound effects and visual elements
            if scene.get("sound_effects"):
                st.write("**Sound Effects:**")
                st.write(" | ".join(scene.get("sound_effects", [])))
            
            if scene.get("visual_elements"):
                st.write("**Visual Elements:**")
                st.write(" | ".join(scene.get("visual_elements", [])))