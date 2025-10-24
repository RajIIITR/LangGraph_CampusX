from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# below code is being referred from Langgarph docs
# stream = chatbot.stream(
#     {'messages': [HumanMessage(content="What is the capital of France?")]},
#     config = {'configurable': {'thread_id': 'thread-1'}},
#     stream_mode = 'messages'
# )
#here stream is a generator object, which we can check using type(stream)

# Since it is a generator we need to use for loop to iterate over it
# The stream has message_chunk and metadata
for message_chunk, metadata in chatbot.stream(
    {'messages': [HumanMessage(content="What is the capital of France?")]},
    config = {'configurable': {'thread_id': 'thread-1'}},
    stream_mode = 'messages'

):
    if message_chunk.content:
        print(message_chunk.content, end = " ", flush = True)

'''
Since we know that we use invoke operation in frontend files so similarly we need to use stream operation in frontend files i.e. no need of invoke or stream code in backend.
So we will use stream operation in frontend files, which we will see in file "lec_13_streamlit_frontend_streaming.py"
'''