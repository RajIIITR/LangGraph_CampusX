import streamlit as st
from lec12_langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid # Its role is to generate unique ids for each session

# ******************************** Utility Functions ******************************** #

# This function will dynamically generate a thread id
def generate_thread_id(): # task 2
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat(): # Task 5
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])    # task 6
    st.session_state["message_history"] = []    # This will help us to clean up the chat.

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

# ******************************** Session Set up ******************************** #
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state: # task 2
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:   # task 6
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])    # Task 6

# ******************************** Sidebar UI ******************************** #
# task 1
st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'): # Task 4
    reset_chat()

st.sidebar.header('My Conversations')

# st.sidebar.text(st.session_state['thread_id'])  #Task 3
# We need to do for loop to print the all chat thread_id in the sidebar
for thread_id in st.session_state["chat_threads"][::-1]:   # Task 7 and we added [::-1] to reverse the list i.e. latest chat will be on top
    # st.sidebar.text(thread_id)    # for Task 7
    if st.sidebar.button(str(thread_id)):   # task 8  'st.sidebar.button(str(thread_id))'
        st.session_state['thread_id'] = thread_id   # Task 9
        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:        # We add this forloop so that we can add the role of user and assistant and get output as per below for loop (1st loop in Main UI)
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        
        st.session_state['message_history'] = temp_messages

# ******************************** Main UI ******************************** #

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#below shows how the output looks like from message_history i.e. backend
#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}} # task 2

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})