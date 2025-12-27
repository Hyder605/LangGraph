from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import test_diffusion_v2
import pathlib
from io import BytesIO
from agent_basev2 import build_workflow
from langgraph.types import Command
import uuid
import base64

app = FastAPI(title="Auto-Manga - Manga Generator API")

# In-memory storage for workflow sessions
sessions = {}

class StoryInput(BaseModel):
    story: str

class StoryEdit(BaseModel):
    session_id: str
    edited_story: str

class SessionResponse(BaseModel):
    session_id: str
    generated_story: str
    status: str

class PanelPrompt(BaseModel):
    panel_number: int
    image_prompt: str

class PromptsResponse(BaseModel):
    session_id: str
    prompts: List[PanelPrompt]

class ImageResponse(BaseModel):
    panel_number: int
    image_base64: str

@app.post("/api/generate", response_model=SessionResponse)
async def generate_story(story_input: StoryInput):
    """
    Generate initial story from user input
    """
    if not story_input.story.strip():
        raise HTTPException(status_code=400, detail="Story cannot be empty")
    
    try:
        # Create unique session
        session_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        
        # Build workflow
        workflow = build_workflow()
        
        # Run initial generation
        initial_state = {
            "input_story": story_input.story,
            "generation_attempts": 0,
            "max_attempts": 5
        }
        
        final_state = workflow.invoke(initial_state, config=config)
        
        generated_story = (
            final_state.get("reviewed_story")
            or final_state.get("refined_story")
            or ""
        )
        
        # Store session data
        sessions[session_id] = {
            "workflow": workflow,
            "config": config,
            "generated_story": generated_story,
            "final_state": final_state
        }
        
        return SessionResponse(
            session_id=session_id,
            generated_story=generated_story,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/approve", response_model=PromptsResponse)
async def approve_story(story_edit: StoryEdit):
    """
    Approve edited story and generate prompts
    """
    if story_edit.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[story_edit.session_id]
        workflow = session["workflow"]
        config = session["config"]
        
        # Resume workflow with edited story
        final_after_review = workflow.invoke(
            Command(resume=story_edit.edited_story),
            config=config
        )
        
        # Extract prompts
        prompts_data = final_after_review.get('manga_image_prompts', {}).get('panel_prompts', [])
        
        if not prompts_data:
            raise HTTPException(status_code=500, detail="No prompts generated")
        
        prompts = [
            PanelPrompt(
                panel_number=p.get('panel_number'),
                image_prompt=p.get('image_prompt')
            )
            for p in prompts_data
        ]
        
        # Update session
        session["prompts"] = prompts_data
        session["final_after_review"] = final_after_review
        
        return PromptsResponse(
            session_id=story_edit.session_id,
            prompts=prompts
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.get("/api/image/{session_id}/{panel_number}")
async def generate_image(session_id: str, panel_number: int):
    """
    Generate image for specific panel
    Returns image as PNG
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    prompts = session.get("prompts", [])
    
    # Find the prompt for this panel
    prompt_text = None
    for p in prompts:
        if p.get('panel_number') == panel_number:
            prompt_text = p.get('image_prompt')
            break
    
    if not prompt_text:
        raise HTTPException(status_code=404, detail=f"Panel {panel_number} not found")
    
    try:
        # Generate image
        image = test_diffusion_v2.generate_image(prompt_text)
        
        # Convert to bytes
        img_io = BytesIO()
        image.save(img_io, format="PNG")
        img_io.seek(0)
        
        return StreamingResponse(img_io, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.get("/api/image-base64/{session_id}/{panel_number}", response_model=ImageResponse)
async def generate_image_base64(session_id: str, panel_number: int):
    """
    Generate image for specific panel and return as base64
    Useful for JSON responses
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    prompts = session.get("prompts", [])
    
    # Find the prompt for this panel
    prompt_text = None
    for p in prompts:
        if p.get('panel_number') == panel_number:
            prompt_text = p.get('image_prompt')
            break
    
    if not prompt_text:
        raise HTTPException(status_code=404, detail=f"Panel {panel_number} not found")
    
    try:
        # Generate image
        image = test_diffusion_v2.generate_image(prompt_text)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return ImageResponse(
            panel_number=panel_number,
            image_base64=img_base64
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session information
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "session_id": session_id,
        "generated_story": session.get("generated_story", ""),
        "has_prompts": "prompts" in session,
        "num_prompts": len(session.get("prompts", []))
    }

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete session and free up memory
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    
    return {"status": "deleted", "session_id": session_id}

@app.get("/")
async def root():
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)