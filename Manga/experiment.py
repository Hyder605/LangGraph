from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated,Literal,List,Optional
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
import operator
import json
import uuid



_: bool = load_dotenv(find_dotenv())

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")



class MangaState(TypedDict):
    input_story:str
    refined_story:str
    extracted_features:dict
    character_feature:dict
    panel_scenes:dict


def feature_extractor(state:MangaState):
    refine_story = state['refined_story']
    prompt = f"""
    You are a manga story analyzer.
    Read the refined story below and extract ALL the most important features
    that will help in turning it into a manga comic.

    - Output must be valid JSON.
    - Choose your own keys and categories (no fixed schema).
    - Be concise and focus on what matters for manga creation. 
      (characters, emotions, visual cues, panel ideas, symbolism, etc.).

    Refined Manga Story: {refine_story}
    """

    output = model.invoke(prompt).content
    return {"extracted_feature": output}


def character_makeup(state: MangaState):
    refined_story = state['refined_story']
    extracted_feature = state['extracted_features']

    # Normalize input
    if isinstance(extracted_feature, dict):
        extracted_feature_json = extracted_feature
    elif isinstance(extracted_feature, str):
        try:
            extracted_feature_json = json.loads(extracted_feature)
        except Exception:
            extracted_feature_json = {"main_characters": [], "character_descriptions": []}
    else:
        extracted_feature_json = {}

    prompt = f"""
    You are a manga character designer.  
    Read the refined story and extracted features, then design detailed manga characters.  

    Task: Produce a JSON object with `"characters"` array.  
    - Each character should have **any attributes you decide are most important** for drawing them in manga style.  
    - Examples of attributes: name, role, appearance, signature poses, emotions, abilities, symbolic motifs, etc.  
    - You may create your own attribute names.  

    Rules:
    - Output ONLY valid JSON.  
    - One profile per entry in `"main_characters"`.  
    - Keep profiles short but descriptive.  
    - Focus on visual/drawing details and storytelling cues.  

    Refined Story:
    {refined_story}

    Extracted Features:
    {json.dumps(extracted_feature_json)}
    """

    output = model.invoke(prompt).content
    return {"character_makeup": output}


def scene_extractor(state: MangaState):
    refined_story = state['refined_story']
    extracted_feature = state['extracted_features']

    # Normalize input
    if isinstance(extracted_feature, dict):
        extracted_feature_json = extracted_feature
    elif isinstance(extracted_feature, str):
        try:
            extracted_feature_json = json.loads(extracted_feature)
        except Exception:
            extracted_feature_json = {}
    else:
        extracted_feature_json = {}

    prompt = f"""
    You are a manga scene director.  
    Your job is to break the refined story into **important scene-level elements** 
    that will guide manga panel creation.  

    🔹 What to do:
    - Extract the **most visually and narratively important aspects** of each scene.  
    - You are free to decide which attributes matter (e.g. location, mood, pacing, 
      symbolic elements, transitions, key poses, effects).  
    - Do NOT force a fixed structure like "scene_number/location/atmosphere" unless 
      it naturally makes sense.  
    - Think like a manga director: capture the essence of how the scene should LOOK and FEEL.  

    🔹 Output format:
    - Return ONLY valid JSON.  
    - Top-level key must be `"scenes"`.  
    - Inside `"scenes"`, each item can have any keys you consider important 
      for manga creation.  
    - Be concise but descriptive.  

    Refined Story:
    {refined_story}

    Extracted Features:
    {json.dumps(extracted_feature_json)}
    """

    output = model.invoke(prompt).content
    return {"scene_features": output}





import json
from typing import Dict, Any

def display_manga_features(features_output: Dict[str, Any]) -> None:
    """Display extracted features in a user-friendly format"""
    print("=" * 60)
    print("🎨 MANGA STORY FEATURES ANALYSIS")
    print("=" * 60)
    
    # Get the extracted features
    extracted_feature = features_output.get("extracted_feature", "")
    
    if isinstance(extracted_feature, str):
        try:
            features_data = json.loads(extracted_feature)
        except json.JSONDecodeError:
            print("❌ Error: Could not parse features as JSON")
            print(f"Raw output: {extracted_feature}")
            return
    else:
        features_data = extracted_feature
    
    # Display each category
    for category, details in features_data.items():
        category_title = category.replace("_", " ").title()
        print(f"\n📋 {category_title}:")
        print("-" * 40)
        
        if isinstance(details, list):
            for i, item in enumerate(details, 1):
                if isinstance(item, dict):
                    print(f"  {i}. {item}")
                else:
                    print(f"  • {item}")
        elif isinstance(details, dict):
            for key, value in details.items():
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"  {details}")
    print()

def display_character_makeup(character_output: Dict[str, Any]) -> None:
    """Display character designs in a user-friendly format"""
    print("=" * 60)
    print("👥 CHARACTER DESIGN PROFILES")
    print("=" * 60)
    
    # Get the character makeup data
    character_makeup = character_output.get("character_makeup", "")
    
    if isinstance(character_makeup, str):
        try:
            character_data = json.loads(character_makeup)
        except json.JSONDecodeError:
            print("❌ Error: Could not parse character data as JSON")
            print(f"Raw output: {character_makeup}")
            return
    else:
        character_data = character_makeup
    
    # Display characters
    characters = character_data.get("characters", [])
    
    if not characters:
        print("❌ No characters found in the data")
        return
    
    for i, character in enumerate(characters, 1):
        print(f"\n🎭 CHARACTER {i}")
        print("-" * 30)
        
        if isinstance(character, dict):
            for attribute, value in character.items():
                attr_name = attribute.replace("_", " ").title()
                
                # Special formatting for different types of data
                if isinstance(value, list):
                    print(f"  {attr_name}:")
                    for item in value:
                        print(f"    • {item}")
                elif isinstance(value, dict):
                    print(f"  {attr_name}:")
                    for sub_key, sub_value in value.items():
                        print(f"    • {sub_key.replace('_', ' ').title()}: {sub_value}")
                else:
                    # For long descriptions, add some formatting
                    if len(str(value)) > 80:
                        print(f"  {attr_name}:")
                        # Split long text into multiple lines
                        words = str(value).split()
                        line = "    "
                        for word in words:
                            if len(line + word) > 76:
                                print(line)
                                line = "    " + word + " "
                            else:
                                line += word + " "
                        if line.strip():
                            print(line)
                    else:
                        print(f"  {attr_name}: {value}")
        else:
            print(f"  {character}")
    print()

def display_scene_features(scene_output: Dict[str, Any]) -> None:
    """Display scene breakdowns in a user-friendly format"""
    print("=" * 60)
    print("🎬 MANGA SCENE BREAKDOWN")
    print("=" * 60)

    # Get the scene features
    scene_data = scene_output.get("scene_features", "")

    if isinstance(scene_data, str):
        try:
            scene_json = json.loads(scene_data)
        except json.JSONDecodeError:
            print("❌ Error: Could not parse scene data as JSON")
            print(f"Raw output: {scene_data}")
            return
    else:
        scene_json = scene_data

    scenes = scene_json.get("scenes", [])

    if not scenes:
        print("❌ No scenes found in the data")
        return

    for scene in scenes:
        scene_number = scene.get("scene_number", "?")
        print(f"\n🎭 SCENE {scene_number}")
        print("-" * 40)

        # Print each key in the scene
        for key, value in scene.items():
            if key == "scene_number":
                continue  # skip, already displayed
            key_name = key.replace("_", " ").title()

            if isinstance(value, list):
                print(f"  {key_name}:")
                for item in value:
                    print(f"    • {item}")
            elif isinstance(value, dict):
                print(f"  {key_name}:")
                for sub_key, sub_value in value.items():
                    print(f"    • {sub_key.replace('_', ' ').title()}: {sub_value}")
            else:
                print(f"  {key_name}: {value}")
    print()


def display_manga_analysis(
    features_output: Dict[str, Any],
    character_output: Dict[str, Any],
    scene_output: Dict[str, Any]
) -> None:
    """Display features, characters, and scenes in a comprehensive format"""
    print("\n" + "🌟" * 20 + " MANGA ANALYSIS RESULTS " + "🌟" * 20)

    # Story-wide features
    display_manga_features(features_output)

    # Character profiles
    display_character_makeup(character_output)

    # Scene breakdowns
    display_scene_features(scene_output)

    print("✨" * 65)
    print("Analysis complete! Ready for manga creation! 🎨📚")
    print("✨" * 65)



story='''
Ibad saw Aisha across the crowded schoolyard, and his heart *POW!* skipped a '
 "beat. [She's...an angel!] He clumsily rushed towards her, tripping over his "
 'own feet – *THUD!* Aisha giggled, her laughter like wind chimes. "H-hello!" '
 'Ibad stammered, face burning crimson. Aisha smiled, and Ibad knew, with '
 'absolute certainty, that his life had irrevocably changed. GYAa!')
'''
features=feature_extractor({"refined_story":story})
character_mkp=character_makeup({"refined_story": story, "extracted_features": features["extracted_feature"]})
scene_features = scene_extractor({
    "refined_story": story,
    "extracted_features": features["extracted_feature"]
})

from pprint import pprint


import json
from typing import Dict, Any

# def display_manga_features(features_output: Dict[str, Any]) -> None:
#     """Display extracted features in a user-friendly format"""
#     print("=" * 60)
#     print("🎨 MANGA STORY FEATURES ANALYSIS")
#     print("=" * 60)
    
#     # Get the extracted features
#     extracted_feature = features_output.get("extracted_feature", "")
    
#     if isinstance(extracted_feature, str):
#         try:
#             features_data = json.loads(extracted_feature)
#         except json.JSONDecodeError:
#             print("❌ Error: Could not parse features as JSON")
#             print(f"Raw output: {extracted_feature}")
#             return
#     else:
#         features_data = extracted_feature
    
#     # Display each category
#     for category, details in features_data.items():
#         category_title = category.replace("_", " ").title()
#         print(f"\n📋 {category_title}:")
#         print("-" * 40)
        
#         if isinstance(details, list):
#             for i, item in enumerate(details, 1):
#                 if isinstance(item, dict):
#                     print(f"  {i}. {item}")
#                 else:
#                     print(f"  • {item}")
#         elif isinstance(details, dict):
#             for key, value in details.items():
#                 print(f"  • {key.replace('_', ' ').title()}: {value}")
#         else:
#             print(f"  {details}")
#     print()

# def display_character_makeup(character_output: Dict[str, Any]) -> None:
#     """Display character designs in a user-friendly format"""
#     print("=" * 60)
#     print("👥 CHARACTER DESIGN PROFILES")
#     print("=" * 60)
    
#     # Get the character makeup data
#     character_makeup = character_output.get("character_makeup", "")
    
#     if isinstance(character_makeup, str):
#         try:
#             character_data = json.loads(character_makeup)
#         except json.JSONDecodeError:
#             print("❌ Error: Could not parse character data as JSON")
#             print(f"Raw output: {character_makeup}")
#             return
#     else:
#         character_data = character_makeup
    
#     # Display characters
#     characters = character_data.get("characters", [])
    
#     if not characters:
#         print("❌ No characters found in the data")
#         return
    
#     for i, character in enumerate(characters, 1):
#         print(f"\n🎭 CHARACTER {i}")
#         print("-" * 30)
        
#         if isinstance(character, dict):
#             for attribute, value in character.items():
#                 attr_name = attribute.replace("_", " ").title()
                
#                 # Special formatting for different types of data
#                 if isinstance(value, list):
#                     print(f"  {attr_name}:")
#                     for item in value:
#                         print(f"    • {item}")
#                 elif isinstance(value, dict):
#                     print(f"  {attr_name}:")
#                     for sub_key, sub_value in value.items():
#                         print(f"    • {sub_key.replace('_', ' ').title()}: {sub_value}")
#                 else:
#                     # For long descriptions, add some formatting
#                     if len(str(value)) > 80:
#                         print(f"  {attr_name}:")
#                         # Split long text into multiple lines
#                         words = str(value).split()
#                         line = "    "
#                         for word in words:
#                             if len(line + word) > 76:
#                                 print(line)
#                                 line = "    " + word + " "
#                             else:
#                                 line += word + " "
#                         if line.strip():
#                             print(line)
#                     else:
#                         print(f"  {attr_name}: {value}")
#         else:
#             print(f"  {character}")
#     print()

# def display_manga_analysis(features_output: Dict[str, Any], character_output: Dict[str, Any]) -> None:
#     """Display both features and characters in a comprehensive format"""
#     print("\n" + "🌟" * 20 + " MANGA ANALYSIS RESULTS " + "🌟" * 20)
    
#     display_manga_features(features_output)
#     display_character_makeup(character_output)
    
#     print("✨" * 65)
#     print("Analysis complete! Ready for manga creation! 🎨📚")
#     print("✨" * 65)

# # Replace your pprint statements with:
# # display_manga_analysis(features, character_mkp)

# Or use them individually:
#display_manga_features(features)
#display_character_makeup(character_mkp)
display_scene_features(scene_features)