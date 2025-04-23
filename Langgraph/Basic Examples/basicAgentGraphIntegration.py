import json
from typing import List, Dict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_ollama.llms import OllamaLLM 
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool

# Define the state structure
# class State(Dict):
#     messages: List[Dict[str, str]]

# # Initialize the StateGraph
# graph_builder = StateGraph(State)

# Initialize the Ollama local model
# local_llm = ChatOllama(model="deepseek-r1:7b")  # Change to 'llama2', 'gemma', etc., if needed
local_llm = ChatOllama(model="llama3.1:8b", verbose=True)

# Define a simple tool function
@tool
def search_weather_tool(query: str) -> str:
    """A mock tool that returns weather info if the user asks about weather."""
    print("in search weather Tool")
    if "weather" in query.lower():
        weather_json = {"desc": "humid", "temp": "110"}
        return json.dumps(weather_json)
        # return "It's sunny and 75 degrees."
    return "I don't have information on that."

@tool
def search_joke_tool(query: str) -> str:
    """A mock tool that returns a joke."""
    print("in search joke Tool")
    if "joke" in query.lower():
        return "Why don’t skeletons fight each other? They don’t have the guts."
    return "I don't have information on that."  # If the tool doesn't handle the query

# # To create a Tool instance manully instead of using the decorator
# search_weather_tool_instance = Tool(
#     name="SearchTool",
#     func=search_weather_tool,
#     description="Provides weather information based on the query."
# )
# search_joke_tool_instance = Tool(
#     name="JokeTool",
#     func=search_joke_tool,
#     description="Provides a joke based on the query."
# )

tools = [search_weather_tool, search_joke_tool]

graph = create_react_agent(model=local_llm, tools=tools)


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# method to interact with llm
def interact(user_input: str):
    inputs = {"messages": [("user", user_input)]}
    print_stream(graph.stream(inputs, stream_mode="values"))


# Example interaction
interact("What's the weather today?")
# interact("Tell me a joke")