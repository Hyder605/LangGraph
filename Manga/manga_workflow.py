"""
Manga Generation Workflow - Python Module
Extracted from agent_base.ipynb for use with Streamlit
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, Literal, List, Optional
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
import operator
import json
import uuid

# Load environment variables
import os
_: bool = load_dotenv(find_dotenv())

# Set API key if not in environment
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDqjOMA44U8w7FNtEFUHLKImRbX7lYyGZI"

# Schemas
class MangaFeatureSchema(BaseModel):
    main_characters: List[str] = Field(
        ..., description="List of main characters in the story, including roles or names."
    )
    character_descriptions: List[str] = Field(
        ..., description="Short descriptions of the characters' traits, personalities, or roles."
    )
    setting: str = Field(
        ..., description="The primary setting or environment where the story takes place."
    )
    conflict_or_goal: str = Field(
        ..., description="The main conflict, tension, or goal driving the story."
    )
    important_objects: List[str] = Field(
        ..., description="Key objects, weapons, or magical items relevant to the story."
    )
    mood_and_tone: List[str] = Field(
        ..., description="Keywords describing the mood and tone of the story (normalized to lowercase)."
    )
    key_sound_effects_and_emotions: List[str] = Field(
        ..., description="Important sound effects (onomatopoeia) and strong emotions expressed in the story."
    )

class CharacterProfile(BaseModel):
    name_or_role: str
    canonical_name: Optional[str]
    age_range: str
    gender_presentation: Optional[str]
    body_type: str
    height: Optional[str]
    face: str
    hair: str
    eyes: str
    clothing: str
    accessories: List[str]
    color_palette: List[str]
    notable_marks: List[str]
    important_objects: List[str]
    signature_poses: List[str]
    default_expressions: List[str]
    voice_short: Optional[str]
    drawing_instructions: str
    visual_reference_prompt: str
    consistency_token: str

class CharacterList(BaseModel):
    characters: List[CharacterProfile] = Field(..., description="List of character profiles")

class SceneFeature(BaseModel):
    scene_number: int
    summary: str
    setting_details: str
    characters_involved: List[str]
    actions: List[str]
    emotions: List[str]
    potential_dialogues: List[str]
    inner_thoughts: List[str]
    sound_effects: List[str]
    visual_elements: List[str]

class SceneFeatureList(BaseModel):
    scenes: List[SceneFeature]

class Director_Panel(BaseModel):
    panel_number: int
    scene_description: str
    characters_present: List[str]
    actions: List[str]
    dialogues: List[str]
    inner_thoughts: List[str]
    sound_effects: List[str]
    visual_elements: List[str]

class MangaPage(BaseModel):
    page_number: int
    panels: List[Director_Panel]

class MangaImagePrompt(BaseModel):
    panel_number: int = Field(..., description="The panel number from the director script")
    image_prompt: str = Field(
        ..., 
        description="Short, clear description of what the image generation model should draw"
    )

class MangaImagePromptPage(BaseModel):
    page_number: int = Field(..., description="Page number in the manga")
    panel_prompts: List[MangaImagePrompt] = Field(
        ..., description="List of image prompts corresponding to panels on this page"
    )

class PanelAnalysis(BaseModel):
    panel_number: int = Field(..., description="Panel number being analyzed")
    quality_score: int = Field(..., ge=1, le=10, description="Quality score from 1-10")
    issues: List[str] = Field(..., description="List of specific problems found")
    strengths: List[str] = Field(..., description="List of good elements")
    needs_improvement: bool = Field(..., description="Whether this panel needs improvement")
    suggested_fixes: List[str] = Field(..., description="Specific improvement suggestions")

class PromptAnalysisResult(BaseModel):
    panel_analyses: List[PanelAnalysis] = Field(..., description="Analysis for each panel")
    overall_score: float = Field(..., description="Average quality score")
    total_panels: int = Field(..., description="Total number of panels")
    panels_needing_improvement: int = Field(..., description="Count of panels needing improvement")
    needs_regeneration: bool = Field(..., description="Whether prompts should be regenerated")
    generation_attempt: int = Field(..., description="Current generation attempt")
    max_attempts_reached: bool = Field(..., description="Whether max attempts reached")

# State definition
class MangaState(TypedDict):
    input_story: str
    refined_story: str
    extracted_features: dict
    character_feature: dict
    scene_features: dict
    panel_scenes: dict
    manga_image_prompts: dict
    prompt_analysis: dict
    generation_attempts: int
    max_attempts: int

# Initialize models
try:
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
    structured_model_MangaFeature = model.with_structured_output(MangaFeatureSchema)
    structured_model_characterList = model.with_structured_output(CharacterList)
    structured_model_director = model.with_structured_output(MangaPage)
    structured_model_scene = model.with_structured_output(SceneFeatureList)
    structured_model_Mangaprompt = model.with_structured_output(MangaImagePromptPage)
    structured_model_PromptAnalysis = model.with_structured_output(PromptAnalysisResult)
except Exception as e:
    print(f"Warning: Could not initialize AI models: {e}")
    # Create dummy models for testing
    class DummyModel:
        def invoke(self, prompt):
            class DummyResponse:
                content = "Dummy response"
                def model_dump(self):
                    return {"dummy": "data"}
            return DummyResponse()
    
    model = DummyModel()
    structured_model_MangaFeature = DummyModel()
    structured_model_characterList = DummyModel()
    structured_model_director = DummyModel()
    structured_model_scene = DummyModel()
    structured_model_Mangaprompt = DummyModel()
    structured_model_PromptAnalysis = DummyModel()

# Workflow functions
def prompt_refiner(state: MangaState):
    user_story = state['input_story']
    prompt = f'''
            You are a professional manga storyteller. 
            Your job is to take a short user query and refine it into a concise manga-style story 
            suitable for ONE PAGE comic (4–6 sentences only).

            Requirements:
            - Keep the story short and dynamic (not more than 6 sentences).
            - Add manga-style elements: 
            * Dramatic emotions 
            * Exaggerated action or reactions 
            * Inner thoughts (marked with brackets [ ])
            * Sound effects (onomatopoeia like "BAM!", "WHOOSH!", "Gyaa!")
            - Story should feel like it can naturally be divided into 4–5 panels later.
            - Do not write panel breakdowns yet.

            User Query: {user_story}

            Refined Manga Story:
            '''
    refine_output = model.invoke(prompt).content
    return {"refined_story": refine_output}

def feature_extractor(state: MangaState):
    refine_story = state['refined_story']
    prompt = f"""
            You are a manga story analyzer. 
            Your task is to read the following refined manga story and extract its key features. 
            You MUST return the result as valid JSON that conforms to the MangaFeatureSchema below:

            Schema:
            {{
            "main_characters": ["list of character names or roles"],
            "character_descriptions": ["list of short character descriptions, same order as main_characters"],
            "setting": "short description of where the story takes place",
            "conflict_or_goal": "one-sentence summary of the story's central conflict or goal",
            "important_objects": ["list of important items, weapons, or artifacts"],
            "mood_and_tone": ["one or more keywords: dramatic, mysterious, adventurous, romantic, comedic, emotional, dark"],
            "key_sound_effects_and_emotions": ["list of notable sound effects (onomatopoeia) and strong emotions"]
            }}

            Rules:
            - Only output valid JSON, no explanations.
            - Keep responses short and concise.
            - Ensure the JSON matches the schema exactly.

            Refined Manga Story:{refine_story}
        """
    output = structured_model_MangaFeature.invoke(prompt)
    return {"extracted_features": output.model_dump()}

def character_makeup(state: MangaState):
    refined_story = state['refined_story']
    extracted_feature = state['extracted_features']

    if isinstance(extracted_feature, dict):
        extracted_feature_json = extracted_feature
    elif isinstance(extracted_feature, str):
        try:
            extracted_feature_json = json.loads(extracted_feature)
        except Exception:
            extracted_feature_json = {"main_characters": [], "character_descriptions": []}
    else:
        extracted_feature_json = {}

    prompt = f'''
        You are a manga character designer. 
        Input: a short refined manga story and the extracted features (characters & brief descriptions).
        Your job: produce a JSON array "characters" of detailed, stable character profiles suitable for repeated drawing across multiple panels.
        You MUST output valid JSON ONLY and match the schema exactly.

        Rules:
        - You MUST create one character profile for every entry in "main_characters".
        - The number of profiles in "characters" must exactly equal the number of "main_characters".
        - Use the paired "character_descriptions" to enrich each profile.
        - If details are missing, infer them from the refined story.
        - Keep each profile short, clear, and usable for consistent drawing.
        - Output only valid JSON in the format: {{ "characters": [ ... ] }}

        Refined Story:
        {refined_story}

        Extracted Features:
        {json.dumps(extracted_feature_json)}
    '''
    output = structured_model_characterList.invoke(prompt)
    return {"character_feature": output.model_dump()}

def scene_feature_extractor(state: MangaState):
    refined_story = state['refined_story']
    extracted_feature = state['extracted_features']
    characters = state['character_feature']

    if isinstance(extracted_feature, dict):
        features_json = extracted_feature
    else:
        try:
            features_json = json.loads(extracted_feature)
        except Exception:
            features_json = {}

    if isinstance(characters, dict):
        characters_json = characters
    else:
        try:
            characters_json = json.loads(characters)
        except Exception:
            characters_json = {}

    prompt = f"""
    You are a Manga Scene Director.  
    Input: a refined short manga story, extracted features, and character profiles.  
    Task: break the story into **4–5 sequential scenes** (not panels yet).  

    Rules:
    - Always output 4 or 5 scenes. Never fewer.  
    - Each scene should feel like it could become one manga panel later.  
    - Use only characters from the character profiles.  
    - Return **valid JSON only**.  

    Refined Story: {refined_story}
    Extracted Features: {json.dumps(features_json)}
    Character Profiles: {json.dumps(characters_json)}
    """

    output = structured_model_scene.invoke(prompt)
    return {"scene_features": output.model_dump()}

def manga_director(state: MangaState):
    refined_story = state['refined_story']
    features = state['extracted_features']
    characters = state['character_feature']
    scenes = state['scene_features']

    prompt = f"""
    You are a Manga Director. 
    Your job is to create a ONE-PAGE manga script divided into **exactly 4–5 panels**.

    Rules:
    - Output **exactly 4 or 5 panels**. Never fewer, never more.
    - Each panel should map to one of the extracted "scenes".
    - Use only characters from the given profiles.
    - Ensure JSON output only, no extra explanation.

    Refined Story: {refined_story}
    Extracted Features: {features}
    Character Profiles: {characters}
    Scene Features: {scenes}
    """

    output = structured_model_director.invoke(prompt)

    if "panels" in output and (len(output["panels"]) < 4 or len(output["panels"]) > 5):
        retry_prompt = prompt + "\n\n⚠️ Reminder: You must output 4–5 panels, not fewer, not more."
        output = structured_model_director.invoke(retry_prompt)

    return {"panel_scenes": output.model_dump()}

def manga_comic_generator(state: MangaState):
    refined_story = state["refined_story"]
    features = state["extracted_features"]
    characters = state["character_feature"]
    scenes = state["scene_features"]
    panels = state["panel_scenes"]

    prompt = f"""
    You are a Manga Illustrator AI.
    Generate compact **manga-style comic panel prompts** (≤70 tokens each).

    Rules:
    - Style: black-and-white manga, clean line art, screentone shading.
    - Characters: always use their "consistency_token" + short visual keywords.
    - Panel prompt must be **1 short sentence**, keyword-style.
    - Always include: camera angle, characters, action, scene, emotions, sound, dialogue.
    - End each with "in consistent manga style".

    Refined Story: {refined_story}
    Extracted Features: {json.dumps(features, indent=2)}
    Character Profiles: {json.dumps(characters, indent=2)}
    Scene Features: {json.dumps(scenes, indent=2)}
    Director's Panel Script: {json.dumps(panels, indent=2)}
    """

    return {"manga_image_prompts": structured_model_Mangaprompt.invoke(prompt).model_dump()}

def prompt_analyzer(state: MangaState):
    """Analyze manga image prompts for quality"""
    prompts_data = state.get("manga_image_prompts", {})
    panel_prompts = prompts_data.get("panel_prompts", [])
    attempts = state.get("generation_attempts", 0)
    max_attempts = state.get("max_attempts", 5)
    
    if not panel_prompts:
        empty_analysis = PromptAnalysisResult(
            panel_analyses=[],
            overall_score=0.0,
            total_panels=0,
            panels_needing_improvement=0,
            needs_regeneration=False,
            generation_attempt=attempts + 1,
            max_attempts_reached=attempts >= max_attempts
        )
        return {
            "prompt_analysis": empty_analysis.model_dump(),
            "generation_attempts": attempts + 1
        }
    
    all_prompts_text = "\n\n".join([
        f"Panel {panel.get('panel_number', i+1)}: {panel.get('image_prompt', '')}"
        for i, panel in enumerate(panel_prompts)
    ])
    
    collective_analysis_prompt = f"""
    You are an expert manga artist and prompt engineer for AI image generation.
    Analyze this COMPLETE MANGA PAGE (all panels together) according to professional manga standards.

    COMPLETE MANGA PAGE TO ANALYZE:
    {all_prompts_text}

    Analyze the ENTIRE PAGE and provide detailed quality assessment.
    """
    
    try:
        full_analysis = structured_model_PromptAnalysis.invoke(collective_analysis_prompt)
        analysis_result = full_analysis.model_dump()
    except Exception as e:
        # Fallback analysis
        fallback_analyses = []
        for i, panel in enumerate(panel_prompts):
            panel_num = panel.get("panel_number", i+1)
            fallback_analyses.append({
                "panel_number": panel_num,
                "quality_score": 7,
                "issues": ["Analysis unavailable"],
                "strengths": ["Contains manga elements"],
                "needs_improvement": False,
                "suggested_fixes": []
            })
        
        analysis_result = {
            "panel_analyses": fallback_analyses,
            "overall_score": 7.0,
            "total_panels": len(panel_prompts),
            "panels_needing_improvement": 0,
            "needs_regeneration": False,
            "generation_attempt": attempts + 1,
            "max_attempts_reached": attempts >= max_attempts
        }
    
    overall_score = analysis_result.get("overall_score", 0)
    panels_needing_improvement = analysis_result.get("panels_needing_improvement", 0)
    
    page_quality_threshold = 7.5
    max_problematic_panels = 1
    
    should_regenerate = (
        (overall_score < page_quality_threshold or panels_needing_improvement > max_problematic_panels)
        and attempts < max_attempts
    )
    
    analysis_result["needs_regeneration"] = should_regenerate
    analysis_result["generation_attempt"] = attempts + 1
    analysis_result["max_attempts_reached"] = attempts >= max_attempts
    
    return {
        "prompt_analysis": analysis_result,
        "generation_attempts": attempts + 1
    }

def should_regenerate_prompts(state: MangaState):
    """Route based on quality analysis"""
    analysis = state.get("prompt_analysis", {})
    needs_regen = analysis.get("needs_regeneration", False)
    overall_score = analysis.get("overall_score", 0)
    max_attempts_reached = analysis.get("max_attempts_reached", False)
    
    if max_attempts_reached:
        return END
    elif needs_regen and overall_score < 9.5:
        return "manga_comic_generator"
    else:
        return END

# Create the workflow
def create_manga_workflow():
    """Create and return the manga generation workflow"""
    
    graph = StateGraph(MangaState)
    
    # Add nodes
    graph.add_node("prompt_refiner", prompt_refiner)
    graph.add_node("feature_extractor", feature_extractor)
    graph.add_node("character_makeup", character_makeup)
    graph.add_node("scene_feature_extractor", scene_feature_extractor) 
    graph.add_node("manga_director", manga_director)
    graph.add_node("manga_comic_generator", manga_comic_generator)
    graph.add_node("prompt_analyzer", prompt_analyzer)
    
    # Add edges
    graph.add_edge(START, "prompt_refiner")
    graph.add_edge("prompt_refiner", "feature_extractor")
    graph.add_edge("feature_extractor", "character_makeup")
    graph.add_edge("character_makeup", "scene_feature_extractor")
    graph.add_edge("scene_feature_extractor", "manga_director")
    graph.add_edge("manga_director", "manga_comic_generator")
    graph.add_edge("manga_comic_generator", "prompt_analyzer")
    
    # Add conditional edge
    graph.add_conditional_edges(
        "prompt_analyzer",
        should_regenerate_prompts,
        {
            "manga_comic_generator": "manga_comic_generator",
            END: END
        }
    )
    
    return graph.compile()

# Create the workflow instance
workflow = create_manga_workflow()

def generate_manga(input_story: str, max_attempts: int = 3) -> dict:
    """
    Main function to generate manga from a story
    
    Args:
        input_story: The input story text
        max_attempts: Maximum number of quality improvement attempts
        
    Returns:
        Dict containing the complete manga generation result
    """
    initial_state = {
        'input_story': input_story,
        'generation_attempts': 0,
        'max_attempts': max_attempts
    }
    
    try:
        final_state = workflow.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"Error in manga generation: {e}")
        # Return a basic state with error info
        return {
            'input_story': input_story,
            'error': str(e),
            'generation_attempts': 0,
            'max_attempts': max_attempts
        }

if __name__ == "__main__":
    # Test the workflow
    test_story = "A boy named Ibad falls in love with a girl named Aisha."
    result = generate_manga(test_story, max_attempts=2)
    print("Manga generation completed!")
    print(f"Final state keys: {list(result.keys())}")