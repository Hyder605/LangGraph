import streamlit as st
import time

class ProgressTracker:
    def __init__(self):
        self.progress = 0
        self.current_step = 0
        self.total_steps = 7  # Total workflow steps
        self.step_names = [
            "Initializing...",
            "Refining Story...",
            "Extracting Features...", 
            "Designing Characters...",
            "Planning Scenes...",
            "Directing Panels...",
            "Generating Prompts...",
            "Quality Analysis..."
        ]

    def update_progress(self, step: int, message: str = ""):
        """Update progress to a specific step"""
        self.current_step = min(step, self.total_steps)
        self.progress = (self.current_step / self.total_steps) * 100
        
        # Display progress bar
        progress_bar = st.progress(self.progress / 100)
        
        # Display current step message
        if message:
            st.write(f"📍 **Step {self.current_step}/{self.total_steps}:** {message}")
        elif step < len(self.step_names):
            st.write(f"📍 **Step {self.current_step}/{self.total_steps}:** {self.step_names[step]}")
        
        return progress_bar

    def increment_progress(self, message: str = ""):
        """Increment progress by one step"""
        return self.update_progress(self.current_step + 1, message)

    def complete_progress(self):
        """Mark progress as complete"""
        self.progress = 100
        self.current_step = self.total_steps
        st.progress(1.0)
        st.success("✅ Generation completed successfully!")

    def reset_progress(self):
        """Reset progress to beginning"""
        self.progress = 0
        self.current_step = 0
        st.progress(0.0)

    def display_status(self, message: str, status_type: str = "info"):
        """Display a status message with different types"""
        if status_type == "success":
            st.success(message)
        elif status_type == "error":
            st.error(message)
        elif status_type == "warning":
            st.warning(message)
        else:
            st.info(message)

    def display_workflow_steps(self):
        """Display all workflow steps with current progress"""
        st.subheader("🔄 Workflow Progress")
        
        for i, step_name in enumerate(self.step_names):
            if i < self.current_step:
                st.write(f"✅ {step_name}")
            elif i == self.current_step:
                st.write(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")

    def simulate_progress(self, container=None):
        """Simulate progress for demo purposes"""
        if container is None:
            container = st.empty()
            
        with container:
            for i, step_name in enumerate(self.step_names):
                self.update_progress(i, step_name)
                time.sleep(0.5)  # Simulate work being done
            
            self.complete_progress()