from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
import operator
import os
from langsmith import traceable

os.environ['LANGCHAIN_PROJECT']="ESSAY CHECK"


_: bool = load_dotenv(find_dotenv())

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")





essay2='''

Climate is the long-term pattern of weather conditions in a particular area. It influences how we live, grow food, and sustain life on Earth. Over the past century, human activities like burning fossil fuels, deforestation, and industrialization have drastically changed the climate, leading to global warming. Rising temperatures cause glaciers to melt, sea levels to rise, and weather patterns to become unpredictable. Floods, droughts, and extreme storms are becoming more frequent and severe, putting communities and ecosystems at risk.

Climate change also threatens biodiversity. Many species cannot adapt quickly enough to shifting habitats and changing conditions. Coral reefs are dying due to ocean warming and acidification. Farmers face challenges as growing seasons shift and water becomes scarce in some regions. To fight climate change, nations must reduce carbon emissions, switch to renewable energy, and protect forests and oceans that absorb carbon dioxide.
'''

class EvaluationSchema(BaseModel):
    feedback:str=Field(description="Detailed feedback for the essay")
    score:int=Field(description='Score out of 10',ge=0,le=10)


Structured_model=model.with_structured_output(EvaluationSchema)

class EssayState(TypedDict):
    essay_text:str
    clarity_feedback:str
    analy_feedback:str
    lang_feedback:str
    summary_feedback:str
    individual_score:Annotated[list[int],operator.add]  ##Reducer Function
    avg_score:float


@traceable(name="evaluate_langauge_fn",tags=["dimension:Language"],metadata={"dimension":"language"})
def evaluate_langauge(state:EssayState)->EssayState:
   
    prompt=f'Evaluate the langauge quality of the following essay and provide a feedback and assign a score out of 10 \n {state["essay_text"]}'

    output=Structured_model.invoke(prompt)
    return {"lang_feedback":output.feedback,'individual_score':[output.score]}


@traceable(name="evaluate_analysis_fn", tags=["dimension:analysis"], metadata={"dimension": "analysis"})
def evaluate_analysis(state:EssayState)->EssayState:
   
    prompt=f'Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n {state["essay_text"]}'

    output=Structured_model.invoke(prompt)
    return {"analy_feedback":output.feedback,'individual_score':[output.score]}

@traceable(name="evaluate_thought_fn", tags=["dimension:clarity"], metadata={"dimension": "clarity_of_thought"})
def evaluate_thought(state:EssayState)->EssayState:
   
    prompt=f'Evaluate the depth of clarity of the following essay and provide a feedback and assign a score out of 10 \n {state["essay_text"]}'

    output=Structured_model.invoke(prompt)
    return {"clarity_feedback":output.feedback,'individual_score':[output.score]}


@traceable(name="final_evaluation_fn", tags=["aggregate"])
def final_evaluation(state:EssayState):
    prompt = f'Based on the following feedbacks create a summarized feedback \n language feedback - {state["lang_feedback"]} \n depth of analysis feedback - {state["analy_feedback"]} \n clarity of thought feedback - {state["clarity_feedback"]}'
    
    overall_feedback = model.invoke(prompt).content

    # avg calculate
    avg_score = sum(state['individual_score'])/len(state['individual_score'])

    return {'summary_feedback': overall_feedback, 'avg_score': avg_score}




graph=StateGraph(EssayState)

##Adding Nodes
graph.add_node('evaluate_language',evaluate_langauge)
graph.add_node('evaluate_analysis',evaluate_analysis)
graph.add_node('evaluate_thought',evaluate_thought)
graph.add_node('final_evaluation',final_evaluation)


##Adding Edges

graph.add_edge(START,'evaluate_language')
graph.add_edge(START,'evaluate_analysis')
graph.add_edge(START,'evaluate_thought')

graph.add_edge('evaluate_language','final_evaluation')
graph.add_edge('evaluate_analysis','final_evaluation')
graph.add_edge('evaluate_thought','final_evaluation')

graph.add_edge('final_evaluation',END)



workflow=graph.compile()


if __name__=="__main__":
    result=workflow.invoke(
        {"essay_text":essay2},
        config={
            "run_name":"evaluate essay",
            "tags":["essay","langraph","evaluation"],
            "metadata":{
                "essay_length":len(essay2),
                "model":"Gemini",
                "dimensions":["langauge","analysis","clarity"],
            
            },
        },
    )
    print("\n=== Evaluation Results ===")
    print("Language feedback:\n", result.get("lang_feedback", ""), "\n")
    print("Analysis feedback:\n", result.get("analy_feedback", ""), "\n")
    print("Clarity feedback:\n", result.get("clarity_feedback", ""), "\n")
    print("Overall feedback:\n", result.get("summary_feedback", ""), "\n")
    print("Individual scores:", result.get("individual_score", []))
    print("Average score:", result.get("avg_score", 0.0))

