from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated,Literal,List,Optional
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
import operator
import json
import uuid



## Schema For Overall Features from the Story
class MangaFeatureSchema(BaseModel):
    main_characters: List[str] = Field(
        ..., description="List of main characters in the story, including roles or names."
    )
    
    character_descriptions: List[str] = Field(
        ..., description="Short descriptions of the characters’ traits, personalities, or roles."
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
    
    mood_and_tone: List[
        Literal["dramatic", "mysterious", "adventurous", "romantic", "comedic", "emotional", "dark"]
    ] = Field(
        ..., description="Keywords describing the mood and tone of the story."
    )
    
    key_sound_effects_and_emotions: List[str] = Field(
        ..., description="Important sound effects (onomatopoeia) and strong emotions expressed in the story."
    )




### Schema for Character description
class CharacterProfile(BaseModel):
    name_or_role: str                 # e.g. "Curious Boy"
    canonical_name: Optional[str]     # e.g. "Taro" (or null)
    age_range: str                    # e.g. "early teens (13-15)"
    gender_presentation: Optional[str]# e.g. "male-presenting" or "non-binary"
    body_type: str                    # e.g. "slim, small frame"
    height: Optional[str]             # e.g. "short" or "170 cm"
    face: str                         # short face description: shape, nose, mouth
    hair: str                         # color, style, length
    eyes: str                         # color, shape, notable features
    clothing: str                     # typical outfit description
    accessories: List[str]            # e.g. ["rope belt", "necklace"]
    color_palette: List[str]          # hex or basic color names, ordered primary → accent
    notable_marks: List[str]          # scars, tattoos, birthmarks
    important_objects: List[str]      # items tied to the character, can be []
    signature_poses: List[str]        # short phrases e.g. ["hand-on-hilt", "heroic stance"]
    default_expressions: List[str]    # e.g. ["wide-eyed shock","determined glare"]
    voice_short: Optional[str]        # quick tonal note for dialogue (e.g. "soft, inquisitive")
    drawing_instructions: str         # manga-specific tips: line weight, shading, typical camera angle
    visual_reference_prompt: str      # 1-2 sentence short prompt formatted for image models
    consistency_token: str            # unique id you can pass to image-generator to keep same character


### For list of characters
class CharacterList(BaseModel):
    characters: List[CharacterProfile] = Field(..., description="List of character profiles"
    )

## Schema For Director
class Director_Panel(BaseModel):
    panel_number: int
    scene_description: str              # What is shown in the panel (setting, action, camera)
    characters_present: List[str]       # From character_setup
    actions: List[str]                  # Key actions happening in this panel
    dialogues: List[str]                # Short speech bubbles, "Name: text"
    inner_thoughts: List[str]           # If any, written as [thoughts]
    sound_effects: List[str]            # Onomatopoeia

## Schema for Number of Pages

class MangaPage(BaseModel):
    page_number: int
    panels: List[Director_Panel]


_: bool = load_dotenv(find_dotenv())

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
structured_model_MangaFeature=model.with_structured_output(MangaFeatureSchema)
structured_model_characterList=model.with_structured_output(CharacterList)
structured_model_director=model.with_structured_output(MangaPage)


class MangaState(TypedDict):
    input_story:str
    refined_story:str
    extracted_features:dict
    character_feature:dict
    directions_dialogue:dict

def prompt_refinner(state:MangaState):
    user_story=state['input_story']
    prompt=f'''
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
    refine_output=model.invoke(prompt).content
    return {"refined_story":refine_output}



def feature_extractor(state:MangaState):
    refine_story=state['refined_story']
    prompt=f"""

            You are a manga story analyzer. 
            Your task is to read the following refined manga story and extract its key features. 
            You MUST return the result as valid JSON that conforms to the MangaFeatureSchema below:

            Schema:
            {{
            "main_characters": ["list of character names or roles"],
            "character_descriptions": ["list of short character descriptions, same order as main_characters"],
            "setting": "short description of where the story takes place",
            "conflict_or_goal": "one-sentence summary of the story’s central conflict or goal",
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
    output=structured_model_MangaFeature.invoke(prompt)

    return {"extracted_feature":output}


def character_makeup(state: MangaState):
    refined_story = state['refined_story']
    extracted_feature = state['extracted_features']

    # Handle different types of extracted_feature
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
        Your job: produce a JSON object with "characters" array containing detailed character profiles.
        You MUST output valid JSON ONLY and match the schema exactly.

        Schema:
        {{
        "characters": [
            {{
            "name_or_role": "string",
            "canonical_name": "string or null",
            "age_range": "string",
            "gender_presentation": "string or null",
            "body_type": "string",
            "height": "string or null",
            "face": "short description (shape, nose, mouth, distinguishing facial features)",
            "hair": "short description (color, style, length)",
            "eyes": "short description (color, shape, special details like glow)",
            "clothing": "short description (top, bottom, shoes, texture)",
            "accessories": ["list of accessories"],
            "color_palette": ["primary", "secondary", "accent"],
            "notable_marks": ["scars, tattoos, birthmarks or empty list"],
            "important_objects": ["items associated with this character"],
            "signature_poses": ["list of 2-4 signature poses"],
            "default_expressions": ["list of 3 typical expressions used in manga"],
            "voice_short": "one-line descriptor of speaking voice or null",
            "drawing_instructions": "manga-specific tips (line weight, shading, preferred camera angles)",
            "visual_reference_prompt": "1-2 sentence prompt for an image generator to draw this character consistently",
            "consistency_token": "unique_short_token (use this in downstream image prompts to ensure consistency)"
            }}
        ]
        }}

        
        Rules:
        - You MUST create one character profile for every entry in "main_characters".
        - The number of profiles in "characters" must exactly equal the number of "main_characters".
        - Use the paired "character_descriptions" to enrich each profile.
        - If details are missing, infer them from the refined story.
        - Keep each profile short, clear, and usable for consistent drawing.
        - Output only valid JSON in the required format.

        Refined Story:
        {refined_story}

        Extracted Features:
        {json.dumps(extracted_feature_json)}

    '''
    
    # Use the new structured model that expects a list
    output = structured_model_characterList.invoke(prompt)
    return {"character_makeup": output}


def manga_director(state: MangaState):
    refined_story = state['refined_story']
    features = state['extracted_feature']
    characters = state['character_makeup']

    prompt = f"""
    You are a Manga Director. 
    Your job is to take the refined story, extracted features, and character profiles, 
    and create a ONE-PAGE manga script divided into **exactly 4–5 panels**.

    Schema:
    {{
      "page_number": 1,
      "panels": [
        {{
          "panel_number": 1,
          "scene_description": "string (describe scene, setting, mood, camera angle)",
          "characters_present": ["list of character names_or_roles"],
          "actions": ["short action phrases"],
          "dialogues": ["Name: text"],
          "inner_thoughts": ["list of inner thoughts if any"],
          "sound_effects": ["list of onomatopoeia like BAM, WHOOSH"]
        }}
      ]
    }}

    Rules:
    - Output **exactly 4 or 5 panels**. Never fewer, never more.
    - "panels" must always be an array with multiple objects (panel_number 1...n).
    - Use only characters from the given profiles.
    - Keep dialogues short, natural, manga-style.
    - Balance between action, emotion, and pacing.
    - Ensure JSON output only, no extra explanation.

    Refined Story: {refined_story}

    Extracted Features: {features}

    Character Profiles: {characters}
    """

    output = structured_model_director.invoke(prompt)

    # ✅ post-check: if less than 4 panels, you can re-call with "retry mode"
    if "panels" in output and len(output["panels"]) < 4:
        # retry enforcement
        retry_prompt = prompt + "\n\n⚠️ Reminder: You must output 4–5 panels, not fewer."
        output = structured_model_director.invoke(retry_prompt)

    return {"manga_page": output}



story=prompt_refinner({'input_story':"A boy name Ibad fall in love with a girl named Aisha."})
features=feature_extractor({"refined_story":story})
character_makeup=character_makeup({"refined_story": story["refined_story"], "extracted_features": features["extracted_feature"]})


from pprint import pprint

pprint((character_makeup['character_makeup']))