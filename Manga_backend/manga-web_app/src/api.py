from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import test_diffusion_v2
import pathlib
from io import BytesIO
from agent_basev2_copy import build_workflow
from langgraph.types import Command
import uuid
import os
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil


app = FastAPI(title="Auto-Manga - Manga Generator API")
# Add this block immediately after creating 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for workflow sessions
sessions = {}


os.makedirs(r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images", exist_ok=True)
# Serve generated images folder as public static files
app.mount(
    "/generated_images",
    StaticFiles(directory=r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images"),
    name="generated_images"
)

class StoryInput(BaseModel):
    story: str
    genre: Optional[str] = None  # "dramatic" or "magical"


class StoryEdit(BaseModel):
    session_id: str
    edited_story: str
    genre: Optional[str] = None  # "dramatic" or "magical"


class SessionResponse(BaseModel):
    session_id: str
    generated_story: str
    status: str

class PanelPrompt(BaseModel):
    panel_number: int
    image_prompt: str
    image_path: Optional[str] = None

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
    

    #shutil.rmtree(r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images")

    if not story_input.story.strip():
        raise HTTPException(status_code=400, detail="Story cannot be empty")
    
    try:
    # if True:
        # Create unique session
        session_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        
        # Build workflow
        workflow = build_workflow()
        
        # Run initial generation
        initial_state = {
            "input_story": story_input.story,
            "genre": story_input.genre, 

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
            "final_state": final_state,
            "genre": story_input.genre
        }
        
        return SessionResponse(
            session_id=session_id,
            generated_story=generated_story,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

import os
from io import BytesIO

@app.post("/api/approve", response_model=PromptsResponse)
async def approve_story(story_edit: StoryEdit):
    """
    Approve edited story, generate prompts, generate all images,
    store images in folder, and return public image URLs.
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
        
        # Extract panel prompts
        prompts_data = final_after_review.get("manga_image_prompts", {}).get("panel_prompts", [])
        
        if not prompts_data:
            raise HTTPException(status_code=500, detail="No prompts generated")

        # Folder where images will be saved
        base_folder = r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images"
        session_folder = os.path.join(base_folder, story_edit.session_id)

        # Create session folder for images
        os.makedirs(session_folder, exist_ok=True)

        # Public URL prefix for images
        public_prefix = f"http://203.241.246.178:8000/generated_images/{story_edit.session_id}"

        updated_panels = []   # Final results list

        # Generate images for every panel
        for panel in prompts_data:
            panel_num = panel.get("panel_number")
            prompt_text = panel.get("image_prompt")

            # File naming
            file_name = f"panel_{panel_num}.png"
            local_path = os.path.join(session_folder, file_name)

            # Public URL returned to frontend
            public_url = f"{public_prefix}/{file_name}"

            try:
                # Generate and store image
                img = test_diffusion_v2.generate_image(prompt_text)
                img.save(local_path, format="PNG")

            except Exception as err:
                print(f"Error generating image for panel {panel_num}: {err}")

            # Save final result
            updated_panels.append(
                PanelPrompt(
                    panel_number=panel_num,
                    image_prompt=prompt_text,
                    image_path=public_url  # return PUBLIC url
                )
            )

        # Save in session
        session["prompts"] = updated_panels
        session["final_after_review"] = final_after_review

        # Return final response
        return PromptsResponse(
            session_id=story_edit.session_id,
            prompts=updated_panels
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")



class PanelRegenerateRequest(BaseModel):
    session_id: str
    panel_number: int
    prompt: str
    refinements: Optional[str] = None

class PanelRegenerateResponse(BaseModel):
    panel_number: int
    image_path: str

@app.post("/api/regenerate-panel", response_model=PanelRegenerateResponse)
async def regenerate_panel(request: PanelRegenerateRequest):
    """
    Regenerate a specific panel with updated prompt and refinements
    """
    print(sessions)
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[request.session_id]
        
        # Combine prompt with refinements if provided
        final_prompt = request.prompt
        if request.refinements and request.refinements.strip():
            final_prompt = f"{request.prompt}\n\nRefinements: {request.refinements}"
        
        # Folder where images will be saved
        base_folder = r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images"
        session_folder = os.path.join(base_folder, request.session_id)
        
        # Create session folder if it doesn't exist
        os.makedirs(session_folder, exist_ok=True)
        



        
        # ------------------------
        # AUTO VERSIONING LOGIC
        # ------------------------
        base_name = f"panel_{request.panel_number}.png"
        
        # Find next available version
        version = 1
        file_name = base_name
        while os.path.exists(os.path.join(session_folder, file_name)):
            file_name = f"panel_{request.panel_number}_{version}.png"
            version += 1
        
        local_path = os.path.join(session_folder, file_name)
        
        # Generate image with the combined prompt
        img = test_diffusion_v2.generate_image(final_prompt)
        img.save(local_path, format="PNG")
        
        # Return public URL
        public_url = f"/generated_images/{request.session_id}/{file_name}"
        
        # Update session prompts if they exist
        if "prompts" in session:
            for panel in session["prompts"]:
                if panel.panel_number == request.panel_number:
                    panel.image_prompt = final_prompt
                    break
        
        return PanelRegenerateResponse(
            panel_number=request.panel_number,
            image_path=public_url,
            
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panel regeneration failed: {str(e)}")


@app.get("api/image/{session_id}/{panel_number}", response_model=ImageResponse)
async def get_image(session_id: str, panel_number: int):
    """
    Display generated image from the already svaed image in Generated_images folder as base64 and prompt
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Folder where images are saved
        base_folder = r"C:\Users\Haider\Desktop\Manga\LangGraph\Manga_backend\auto-manga-react-app\src\generated_images"
        session_folder = os.path.join(base_folder, session_id)
        
        file_name = f"panel_{panel_number}.png"
        local_path = os.path.join(session_folder, file_name)
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Read image and convert to base64
        with open(local_path, "rb") as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return ImageResponse(
            panel_number=panel_number,
            image_base64=img_base64
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image retrieval failed: {str(e)}")
   
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
            # "GET /api/image/{session_id}/{panel_number}": "Generate image (PNG)",
            # "GET /api/image-base64/{session_id}/{panel_number}": "Generate image (base64)",
            "GET /api/session/{session_id}": "Get session info",
            "DELETE /api/session/{session_id}": "Delete session"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)