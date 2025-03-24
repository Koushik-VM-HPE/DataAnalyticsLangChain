from langchain.agents import Tool, initialize_agent, AgentType
from langchain_ollama.llms import OllamaLLM


llm = OllamaLLM(model="deepseek-r1:7b")
# Step 1: Define a simple method (function) for addition
def add(num1, num2):
    """A simple function to add two numbers."""
    return num1 + num2

# Step 2: Wrap the function into a LangChain Tool
add_tool = Tool(
    name="AddTool",
    func=add,  # Link the `add` function here
    description="A tool to add two numbers."
)

# Step 3: Set up LangChain Agent

tools = [add_tool]

# Initialize the agent with the tool
agent = initialize_agent(
    tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Step 4: Test the agent with a query
query = "What is 25 plus 30?"
response = agent.run(query)

# Print the result
print(response)
