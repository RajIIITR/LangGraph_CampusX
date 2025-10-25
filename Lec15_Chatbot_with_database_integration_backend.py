from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database="chatbot.db", check_same_thread = False)  # Since we are working with multiple thread hence it should be False
# Checkpointer
checkpointer = SqliteSaver(conn = conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()  # This will store only unique thread so that in frontend we have unique thread which we can create/re-access/update
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

        return list(all_threads)
# # Test

# CONFIG = {'configurable': {'thread_id': 'thread-2'}}

# response = chatbot.invoke(
#     {'messages': [{'role': 'user', 'content': 'Can you tell me about myself?'}]},
#     config=CONFIG
# )

# print(response)