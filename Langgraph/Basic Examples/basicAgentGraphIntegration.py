import json
from typing import List, Dict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_ollama.llms import OllamaLLM 
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate

# Initialize the Ollama local model
# local_llm = ChatOllama(model="deepseek-r1:7b")  # Change to 'llama2', 'gemma', etc., if needed
local_llm = ChatOllama(model="llama3.1:8b", verbose=True)

# Define a simple tool function
@tool
def search_weather_tool(query: str) -> str:
    """A mock tool that returns weather info if the user asks about weather."""
    print("in search weather Tool")
    # if "weather" in query.lower():
    weather_json = {"desc": "cold", "temp": "50"}
    return json.dumps(weather_json)
        # return "It's sunny and 75 degrees."
    # return "I don't have information on that."

@tool
def search_joke_tool(query: str) -> str:
    """A mock tool that returns a joke."""
    print("in search joke Tool")
    if "joke" in query.lower():
        return "Why don’t skeletons fight each other? They don’t have the guts."
    return "I don't have information on that."  # If the tool doesn't handle the query

tools = [search_weather_tool, search_joke_tool]
tool_names = ["search_weather_tool", "search_joke_tool"]

graph = create_react_agent(model=local_llm, tools=tools)


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        print("####### Printing Stream")
        if isinstance(message, tuple):
            print(f"####### message is : {message}")
        else:
            print("####### pretty print output:")
            message.pretty_print()

# method to interact with llm
def interact(user_input: str):
    inputs = {"messages": [("user", user_input)]}
    print_stream(graph.stream(inputs, stream_mode="values"))

def new_interact(user_input: str):
    template = '''Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}'''

    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(tools=tools, tool_names=tool_names, input = user_input, agent_scratchpad = "scratchpad work for agent thinking process:")

    inputs = {"messages": [("user", formatted_prompt)]}
    print_stream(graph.stream(inputs, stream_mode="values"))

# Example interaction
new_interact("What's the weather today?")
# interact("Tell me a joke")