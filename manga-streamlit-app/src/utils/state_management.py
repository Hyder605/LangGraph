import streamlit as st
import json
import os
from typing import Any, Dict
from pathlib import Path

class StateManager:
    def __init__(self):
        self.state: Dict[str, Any] = {
            "input_story": "",
            "generation_attempts": 0,
            "max_attempts": 5,
            "refined_story": "",
            "extracted_features": {},
            "character_feature": {},
            "scene_features": {},
            "panel_scenes": {},
            "manga_image_prompts": {},
            "prompt_analysis": {},
            "generation_complete": False
        }

    def update_state(self, key: str, value: Any) -> None:
        """Update a specific state key with a new value"""
        self.state[key] = value

    def get_state(self) -> Dict[str, Any]:
        """Get the complete state dictionary"""
        return self.state.copy()

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a specific state value"""
        return self.state.get(key, default)

    def reset_state(self) -> None:
        """Reset state to initial values"""
        self.__init__()

    def save_to_file(self, filepath: str) -> bool:
        """Save current state to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            return True
        except Exception as e:
            st.error(f"Failed to save state: {e}")
            return False

    def load_from_file(self, filepath: str) -> bool:
        """Load state from a JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.state.update(json.load(f))
                return True
            return False
        except Exception as e:
            st.error(f"Failed to load state: {e}")
            return False

    def export_results(self) -> Dict[str, Any]:
        """Export key results for download/sharing"""
        return {
            "input_story": self.state.get("input_story", ""),
            "refined_story": self.state.get("refined_story", ""),
            "characters": self.state.get("character_feature", {}),
            "manga_panels": self.state.get("manga_image_prompts", {}),
            "quality_analysis": self.state.get("prompt_analysis", {}),
            "generation_attempts": self.state.get("generation_attempts", 0)
        }

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of the generation process"""
        analysis = self.state.get("prompt_analysis", {})
        panels = self.state.get("manga_image_prompts", {}).get("panel_prompts", [])
        
        return {
            "total_panels": len(panels),
            "overall_quality": analysis.get("overall_score", 0),
            "generation_attempts": self.state.get("generation_attempts", 0),
            "max_attempts": self.state.get("max_attempts", 5),
            "characters_created": len(self.state.get("character_feature", {}).get("characters", [])),
            "story_length": len(self.state.get("input_story", "")),
            "refined_story_length": len(self.state.get("refined_story", ""))
        }

# Legacy functions for compatibility
def load_state() -> Dict[str, Any]:
    """Load state from session state or return empty state"""
    if 'state_manager' in st.session_state:
        return st.session_state.state_manager.get_state()
    return {}

def save_state(state_data: Dict[str, Any]) -> None:
    """Save state to session state"""
    if 'state_manager' not in st.session_state:
        st.session_state.state_manager = StateManager()
    
    for key, value in state_data.items():
        st.session_state.state_manager.update_state(key, value)