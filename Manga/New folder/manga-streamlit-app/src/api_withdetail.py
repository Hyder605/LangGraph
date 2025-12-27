# IMPORTS SECTION
# FastAPI: Main framework class for building the API
# HTTPException: Used to return HTTP error responses (404, 500, etc.)
# BackgroundTasks: For running tasks in background (imported but not used here)
from fastapi import FastAPI, HTTPException, BackgroundTasks

# StreamingResponse: Used to stream file data (like images) to the client
from fastapi.responses import StreamingResponse

# BaseModel: Pydantic class for defining request/response data structures with validation
from pydantic import BaseModel

# Type hints for better code documentation and IDE support
from typing import Optional, List, Dict, Any

# Your custom module for generating images using diffusion models
import test_diffusion_v2

# pathlib: Modern way to handle file paths (not actively used in this code)
import pathlib

# BytesIO: Creates an in-memory binary stream (used to handle images without disk I/O)
from io import BytesIO

# Your custom workflow builder that creates the LangGraph workflow
from agent_basev2 import build_workflow

# Command: LangGraph class to control workflow execution (resume interrupted workflows)
from langgraph.types import Command

# uuid: Generates unique identifiers for sessions
import uuid

# base64: Encodes binary data (images) into text format for JSON responses
import base64

# Create the FastAPI application instance
# title: Shows up in the auto-generated API documentation
app = FastAPI(title="Manga Prompt Generator API")

# GLOBAL DICTIONARY: Stores all active user sessions
# Structure: {session_id: {workflow, config, generated_story, prompts, etc.}}
# This is in-memory storage - data is lost when server restarts
# For production, you'd use Redis or a database instead
sessions = {}

# PYDANTIC MODELS: Define the structure of request/response data
# These provide automatic validation and documentation

# Model for the initial story input from user
class StoryInput(BaseModel):
    story: str  # The user's story text - required field

# Model for when user edits and approves the story
class StoryEdit(BaseModel):
    session_id: str        # Which session this edit belongs to
    edited_story: str      # The user's edited version of the story

# Response model after story generation
class SessionResponse(BaseModel):
    session_id: str        # Unique ID to track this conversation
    generated_story: str   # The AI-generated story
    status: str           # Status message (e.g., "success")

# Model for a single panel's prompt
class PanelPrompt(BaseModel):
    panel_number: int      # Which panel this is (1, 2, 3...)
    image_prompt: str      # The text prompt to generate the image

# Response containing all panel prompts
class PromptsResponse(BaseModel):
    session_id: str              # Session this belongs to
    prompts: List[PanelPrompt]   # List of all panel prompts

# Response containing a generated image as base64
class ImageResponse(BaseModel):
    panel_number: int      # Which panel this image is for
    image_base64: str      # The image encoded as base64 text

# ENDPOINT 1: Generate initial story
# @app.post: Defines a POST endpoint at /api/generate
# response_model: Tells FastAPI what structure the response will have
@app.post("/api/generate", response_model=SessionResponse)
async def generate_story(story_input: StoryInput):
    """
    Generate initial story from user input
    
    Flow:
    1. User sends their story
    2. API generates an improved/refined version
    3. Returns session_id to track this conversation
    """
    
    # Validate input: Check if story is empty or just whitespace
    if not story_input.story.strip():
        # Raise 400 Bad Request error if story is empty
        raise HTTPException(status_code=400, detail="Story cannot be empty")
    
    # try-except: Catch any errors during processing
    try:
        # Generate a unique identifier for this session
        # Example: "550e8400-e29b-41d4-a716-446655440000"
        session_id = str(uuid.uuid4())
        
        # Create configuration dict for LangGraph
        # thread_id: Allows LangGraph to maintain conversation state
        config = {"configurable": {"thread_id": session_id}}
        
        # Build the LangGraph workflow from your agent_basev2.py
        # This creates the state machine for story processing
        workflow = build_workflow()
        
        # Prepare initial state for the workflow
        initial_state = {
            "input_story": story_input.story,  # User's original story
            "generation_attempts": 0,           # Counter for retry attempts
            "max_attempts": 5                   # Maximum retries allowed
        }
        
        # Execute the workflow with the initial state
        # This runs all the nodes (generate, review, refine, etc.)
        # Returns the final state after all processing
        final_state = workflow.invoke(initial_state, config=config)
        
        # Extract the generated story from final state
        # Try "reviewed_story" first, fall back to "refined_story", or empty string
        # The "or" chain returns the first non-empty value
        generated_story = (
            final_state.get("reviewed_story")
            or final_state.get("refined_story")
            or ""
        )
        
        # Store everything in the sessions dictionary for later use
        sessions[session_id] = {
            "workflow": workflow,              # Save workflow instance for resuming
            "config": config,                  # Save config for consistency
            "generated_story": generated_story, # Save the generated story
            "final_state": final_state         # Save entire state for debugging
        }
        
        # Return successful response with session ID and story
        return SessionResponse(
            session_id=session_id,
            generated_story=generated_story,
            status="success"
        )
    
    # Catch any exception that occurs during processing
    except Exception as e:
        # Return 500 Internal Server Error with error message
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# ENDPOINT 2: Approve edited story and generate image prompts
@app.post("/api/approve", response_model=PromptsResponse)
async def approve_story(story_edit: StoryEdit):
    """
    Approve edited story and generate prompts
    
    Flow:
    1. User edits the generated story
    2. User clicks "approve"
    3. Workflow resumes and generates panel prompts
    4. Returns list of prompts for each manga panel
    """
    
    # Check if this session exists in our storage
    if story_edit.session_id not in sessions:
        # Return 404 Not Found if session doesn't exist
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Retrieve the saved session data
        session = sessions[story_edit.session_id]
        
        # Get the workflow instance we saved earlier
        workflow = session["workflow"]
        
        # Get the config to maintain thread continuity
        config = session["config"]
        
        # Resume the workflow with user's edited story
        # Command(resume=...) tells LangGraph to continue from where it paused
        # This is where the workflow picks up after human approval
        final_after_review = workflow.invoke(
            Command(resume=story_edit.edited_story),
            config=config
        )
        
        # Extract panel prompts from the workflow output
        # .get() with default {} prevents KeyError if key doesn't exist
        # .get('panel_prompts', []) returns empty list if no prompts
        prompts_data = final_after_review.get('manga_image_prompts', {}).get('panel_prompts', [])
        
        # Validate that prompts were actually generated
        if not prompts_data:
            raise HTTPException(status_code=500, detail="No prompts generated")
        
        # Transform raw prompt data into PanelPrompt objects
        # List comprehension: iterate through prompts_data and create PanelPrompt for each
        prompts = [
            PanelPrompt(
                panel_number=p.get('panel_number'),  # Extract panel number
                image_prompt=p.get('image_prompt')   # Extract prompt text
            )
            for p in prompts_data  # For each prompt in the list
        ]
        
        # Update session with new data
        session["prompts"] = prompts_data                      # Save raw prompts
        session["final_after_review"] = final_after_review     # Save full state
        
        # Return the prompts to the client
        return PromptsResponse(
            session_id=story_edit.session_id,
            prompts=prompts
        )
    
    # Re-raise HTTPException without wrapping it
    except HTTPException:
        raise
    
    # Catch any other exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

# ENDPOINT 3: Generate and return image as PNG file
# @app.get: This is a GET request (retrieve data)
# Path parameters: {session_id} and {panel_number} extracted from URL
@app.get("/api/image/{session_id}/{panel_number}")
async def generate_image(session_id: str, panel_number: int):
    """
    Generate image for specific panel
    Returns image as PNG
    
    Example: GET /api/image/abc123/1
    This generates the image for panel 1 of session abc123
    """
    
    # Verify session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Retrieve session data
    session = sessions[session_id]
    
    # Get the list of prompts from session
    # Default to empty list if no prompts exist
    prompts = session.get("prompts", [])
    
    # Find the specific prompt for the requested panel number
    prompt_text = None  # Initialize as None
    
    # Loop through all prompts to find matching panel
    for p in prompts:
        if p.get('panel_number') == panel_number:
            prompt_text = p.get('image_prompt')  # Found it!
            break  # Exit loop early - no need to continue
    
    # If we didn't find the panel, return error
    if not prompt_text:
        raise HTTPException(status_code=404, detail=f"Panel {panel_number} not found")
    
    try:
        # Call your diffusion model to generate the image
        # This returns a PIL Image object
        image = test_diffusion_v2.generate_image(prompt_text)
        
        # Create an in-memory binary stream (like a file, but in RAM)
        img_io = BytesIO()
        
        # Save the PIL Image to the in-memory stream as PNG
        # format="PNG": Specifies the image format
        image.save(img_io, format="PNG")
        
        # Reset stream position to beginning
        # This is necessary because save() moves the pointer to the end
        img_io.seek(0)
        
        # Return the image as a streaming response
        # StreamingResponse: Sends the image data to client
        # media_type: Tells browser this is a PNG image
        return StreamingResponse(img_io, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# ENDPOINT 4: Generate image and return as base64 text
# Alternative to PNG endpoint - useful for JSON APIs
@app.get("/api/image-base64/{session_id}/{panel_number}", response_model=ImageResponse)
async def generate_image_base64(session_id: str, panel_number: int):
    """
    Generate image for specific panel and return as base64
    Useful for JSON responses
    
    Base64: Converts binary image data into text format
    This allows embedding images in JSON responses
    """
    
    # Same validation as previous endpoint
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    prompts = session.get("prompts", [])
    
    # Find the prompt for this panel (same logic as before)
    prompt_text = None
    for p in prompts:
        if p.get('panel_number') == panel_number:
            prompt_text = p.get('image_prompt')
            break
    
    if not prompt_text:
        raise HTTPException(status_code=404, detail=f"Panel {panel_number} not found")
    
    try:
        # Generate image using diffusion model
        image = test_diffusion_v2.generate_image(prompt_text)
        
        # Create in-memory buffer for the image
        buffered = BytesIO()
        
        # Save image to buffer as PNG
        image.save(buffered, format="PNG")
        
        # Get the binary data from buffer
        # .getvalue() returns all bytes from the BytesIO object
        binary_data = buffered.getvalue()
        
        # Encode binary data to base64 string
        # base64.b64encode(): Converts bytes to base64 bytes
        # .decode(): Converts base64 bytes to string
        img_base64 = base64.b64encode(binary_data).decode()
        
        # Return as JSON response with base64 string
        return ImageResponse(
            panel_number=panel_number,
            image_base64=img_base64
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# ENDPOINT 5: Get information about a session
# Useful for checking if a session exists and what state it's in
@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session information
    
    Returns metadata about the session without returning large data
    Useful for debugging or checking session status
    """
    
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get session data
    session = sessions[session_id]
    
    # Return summary information about the session
    return {
        "session_id": session_id,
        "generated_story": session.get("generated_story", ""),
        "has_prompts": "prompts" in session,  # Boolean: True if prompts exist
        "num_prompts": len(session.get("prompts", []))  # Count of prompts
    }

# ENDPOINT 6: Delete a session to free memory
# Important for cleaning up old sessions in production
@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete session and free up memory
    
    Why this is important:
    - Each session stores workflow, images, and state in memory
    - Without cleanup, memory usage grows indefinitely
    - In production, implement automatic cleanup after X hours/days
    """
    
    # Check if session exists before trying to delete
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete the session from the dictionary
    # This removes the reference and allows Python's garbage collector to free memory
    del sessions[session_id]
    
    # Return confirmation
    return {"status": "deleted", "session_id": session_id}

# ENDPOINT 7: Root endpoint - API documentation
# This is what users see when they visit http://localhost:8000/
@app.get("/")
async def root():
    """
    Root endpoint that provides API overview
    
    Helps developers understand available endpoints
    """
    return {
        "message": "Manga Prompt Generator API",
        "endpoints": {
            "POST /api/generate": "Generate story from input",
            "POST /api/approve": "Approve edited story and get prompts",
            "GET /api/image/{session_id}/{panel_number}": "Generate image (PNG)",
            "GET /api/image-base64/{session_id}/{panel_number}": "Generate image (base64)",
            "GET /api/session/{session_id}": "Get session info",
            "DELETE /api/session/{session_id}": "Delete session"
        }
    }

# MAIN EXECUTION BLOCK
# This runs only when you execute this file directly
# (Not when importing it as a module)
if __name__ == "__main__":
    # Import uvicorn: ASGI server that runs FastAPI apps
    import uvicorn
    
    # Start the server
    # app: The FastAPI application instance we created above
    # host="0.0.0.0": Listen on all network interfaces
    #                 - Allows access from other machines
    #                 - Use "127.0.0.1" for localhost-only
    # port=8000: The port number to listen on
    #            - Access at http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)