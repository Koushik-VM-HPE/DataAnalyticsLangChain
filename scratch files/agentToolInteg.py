import json
from langchain.tools import tool
from langchain_core.output_parsers.json import SimpleJsonOutputParser
from langchain.agents import initialize_agent, AgentType
from langchain_ollama.llms import OllamaLLM



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

# Initialize the JSON output parser
parser = SimpleJsonOutputParser()

# Initialize the LLM
llm = OllamaLLM(model="deepseek-r1:7b")

# Initialize the agent with the tool
agent = initialize_agent(
    tools=[get_sample_data],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # The agent decides when to use the tool
    verbose=True
)

# Example query asking for specific JSON fields
query = "Use the 'get_sample_data' tool to provide the sample data."

# Invoke the agent
response = agent.invoke({"input": query})

print(f"response output from agent is : {response}")

# # Parse the output JSON into a Python dictionary
# parsed_data = parser.parse(response["output"])

# # Extract required fields
# print(f"User: {parsed_data['name']}, Role: {parsed_data['role']}")
