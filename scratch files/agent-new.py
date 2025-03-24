import json
from typing import Annotated, TypedDict, Union
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_ollama.llms import OllamaLLM
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
# from langgraph.prebuilt import ToolExecutor, ToolInvocation
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
# from langgraph.prebuilt import ToolExecutor, ToolInvocation

# Define a simple tool that returns hardcoded JSON
@tool
def get_sample_data():
    """
    Returns a hardcoded JSON response with user details.

    Args:
    no parameter for this method

    output:
    Json string of a sample output data
    """
    return json.dumps({
        "id": "12345",
        "name": "Alice Johnson",
        "role": "Software Engineer",
        "company": "Google",
        "joined": 2022
    })

@tool
def get_lorum_ipsum() -> str:
    """
    returns sample lorum ipsum text
    
    args:
    no input parameters for this method

    output:
    string reponse of sample text
    """
    return "random text from for validation"

tools = [get_sample_data, get_lorum_ipsum]

# tool_executor = ToolExecutor(tools)

# Initialize the LLM
llm = OllamaLLM(model="deepseek-r1:7b")

# Initialize the agent with the tool
memory = MemorySaver()
# agent_executor = create_react_agent(llm, tools=[get_sample_data], checkpointer=memory)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS,  # The agent decides when to use the tool
    verbose=True,
    handle_parsing_errors=True 
)

# Example query asking for specific JSON fields
# query = "Please use the 'get_sample_data' tool and give me the exact data in the JSON format."
query = "give me a sample lorum ipsum text."

prompt_template = f""

# Invoke the agent
response = agent.invoke({"input": query})
print(f"LLM raw response: {response}")

# print(f"Response output from agent is: {response['output']}")

# # Optionally parse the output JSON into a Python dictionary if needed
# parsed_data = json.loads(response['output'])

# # Extract required fields
# print(f"User: {parsed_data['name']}, Role: {parsed_data['role']}")
