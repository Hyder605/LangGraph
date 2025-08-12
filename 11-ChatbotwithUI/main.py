from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage
from typing import Annotated, TypedDict
from dotenv import load_dotenv
import os
from sse_starlette.sse import EventSourceResponse  # optional helper package
import asyncio
import json

load_dotenv()

# LangGraph setup
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

class ChatBotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_bot(state: ChatBotState):
    message = state['messages']
    response = model.invoke(message)
    return {"messages": response}

checkpointer = MemorySaver()
graph = StateGraph(ChatBotState)
graph.add_node("chat_bot", chat_bot)
graph.add_edge(START, "chat_bot")
graph.add_edge("chat_bot", END)
workflow = graph.compile()

# FastAPI setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ChatInput(BaseModel):
    user_input: str





@app.post("/chat")
async def chat_endpoint(input_data: ChatInput):
    try:
        #without Streaming
        result = workflow.invoke({"messages": [HumanMessage(content=input_data.user_input)]},config={"configurable": {"thread_id": "user-123"}})
        print("Result:", result)  # Print full result
        return {"response": result["messages"][1].content}
    except Exception as e:
        print("🔥 ERROR:", e)
        return {"response": f"Internal Error: {str(e)}"}

# @app.post("/chat/stream")
# async def chat_stream(input_data: ChatInput):
#     async def event_generator():
#         try:
#             # If workflow.stream is an async generator
#             async for message_chunk, metadata in workflow.stream(
#                 {"messages": [HumanMessage(content=input_data.user_input)]},
#                 config={"configurable": {"thread_id": "user-123"}},
#                 stream_mode="messages"
#             ):
#                 # message_chunk.content may be None sometimes
#                 content = getattr(message_chunk, "content", None)
#                 if content:
#                     # yield an SSE event (client receives this chunk)
#                     yield f"data: {json.dumps({'chunk': content})}\n\n"
#                 await asyncio.sleep(0)  # give back control
#             # EOF event
#             yield "event: done\ndata: {}\n\n"
#         except Exception as e:
#             print("Stream ERROR:", e)
#             yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

#     # Use EventSourceResponse (sse_starlette) or StreamingResponse with correct content-type
#     return EventSourceResponse(event_generator())