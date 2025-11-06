from langgraph.graph import StateGraph
import json

def run_workflow(initial_state):
    from agent_basev2 import build_workflow  # Import the workflow builder from agent_basev2

    workflow = build_workflow()
    final_state = workflow.invoke(initial_state)
    return final_state

def get_image_prompts(final_state):
    return final_state.get('manga_image_prompts', {}).get('panel_prompts', [])

def format_prompts(prompts):
    formatted_prompts = []
    for prompt in prompts:
        formatted_prompts.append({
            "panel_number": prompt['panel_number'],
            "image_prompt": prompt['image_prompt']
        })
    return formatted_prompts

def save_state_to_json(state, filename='state.json'):
    with open(filename, 'w') as f:
        json.dump(state, f, indent=2)