import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage
import uuid
from backend import retrieve_all_threads


################Utility Fucntion####################

def generate_thread():
    thread_id=uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id=generate_thread()
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state["message_history"]=[]


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state['chat_threads'].append(thread_id)


def load_conv(thread_id):
    state=chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])  # default to empty list if missing
    return messages



#########SESSION SETUP#################################
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=generate_thread()


if "chat_threads" not in st.session_state:
    # st.session_state['chat_threads']=[]
    st.session_state['chat_threads']=retrieve_all_threads()



add_thread(st.session_state['thread_id'])

# st.session_state -> dict -> 
# CONFIG = {'configurable': {'thread_id': st.session_state["thread_id"]}}


###Changing the config for Langsmith-->> it will create tracing for each threads seperately, otherwise all trace will be in one window
CONFIG = {
    'configurable': {'thread_id': st.session_state["thread_id"]},
    'metadata':{
        "thread_id": st.session_state["thread_id"]
    },
    "run_name":"chat_turn"
    
    }


############################SIDE BAR###############################
st.sidebar.title("ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My conversation")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_conv(thread_id)
        
        temp_messages=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role="user"
            else:
                role="assistant"
            temp_messages.append({'role':role,'content':msg.content})
        
        st.session_state['message_history']=temp_messages



############################ MAIN UI ###########################

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    
    # ai_message = response['messages'][-1].content
    # # first add the message to message_history
    # st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    # with st.chat_message('assistant'):
    #     st.text(ai_message)

    # with st.chat_message('assistant'):
    #     ai_message=st.write_stream(
    #         message_chunk.content for message_chunk,metadata in chatbot.stream(
    #             {'messages':[HumanMessage(content=user_input)]},
    #             config=CONFIG,
    #             stream_mode="messages"
    #         )
    #     )

    with st.chat_message('assistant'):
        def ai_message():
            for message_chunk,metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk,AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_message())
        
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})


