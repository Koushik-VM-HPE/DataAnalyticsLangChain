import json, os
from typing import List, Dict
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_ollama.llms import OllamaLLM 
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, PromptTemplate
import boto3
from boto3.dynamodb.conditions import Key, And, Attr
from dynamoDBUtils import DynamoDBUtils

# Load environment variables from .env file
load_dotenv()

# Initialize the Ollama local model
local_llm = ChatOllama(model="llama3.1:8b", verbose=True)

# Initialize DynamoDB client
dynamodb_client = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_DB_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_DB_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DB_REGION')
)

# Define a simple tool function
@tool
def search_weather_tool(query: str) -> str:
    """A mock tool that returns weather info if the user asks about weather."""
    print("###################### in search weather Tool")
    # if "weather" in query.lower():
    weather_json = {"desc": "cold", "temp": "50"}
    return json.dumps(weather_json)
        # return "It's sunny and 75 degrees."
    # return "I don't have information on that."

cluster_table = dynamodb_client.Table("devex_ocm_dev")  # type: ignore
cluster_table_hash_key = "tenantID_siteID"
cluster_table_range_key = "clusterID"

@tool
def construct_filter_for_list_clusters(attribute: str = "", value: str = "", limit: int = 10):
    """
    List clusters from the database based on attribute and value filter.
    
    Parameters:
    - attribute: Name of the attribute to filter on (e.g. "clusterName", "available")
    - value: Value to match for the attribute (e.g. "st0322", "true")
    - limit: Maximum number of results to return (default: 10)
    
    Examples:
    - To find clusters with name st0322: attribute="clusterName", value="st0322"
    - To find available clusters: attribute="available", value="true"
    
    Returns:
    List of matching cluster items.
    """
    print(f"########### filter expresion is {attribute} and {value}")
    try:
        # table = dynamodb_client.Table("devex_ocm_dev")  # type: ignore
        # hash_key_name = cluster_table_hash_key
        # range_key_name = cluster_table_range_key
        # # Base condition (hash key)
        # key_condition = Key(hash_key_name).eq(hash_key_value)

        # # Add range key condition if provided
        # if range_key_name and range_key_value:
        #     key_condition = And(key_condition, Key(range_key_name).eq(range_key_value))

        print(f"########### filter expresion is {attribute} and {value}")
         # Convert simple key-value filters to DynamoDB Attr expressions
        dynamodb_filter = None
        if attribute and value:
            dynamodb_filter = {
                attribute: Attr(attribute).eq(value)
            }

        print(f"########### DB filter expresion is {dynamodb_filter}")

        items = DynamoDBUtils.scan(table_name="devex_ocm_intg", filter=dynamodb_filter, limit=limit)

        return items
        # return dynamodb_filter

    except Exception as e:
        print(f"Error fetching data: {e}")
        # return ""
        return []


# Update tools list
tools = [construct_filter_for_list_clusters, search_weather_tool]
tool_names = ["construct_filter_for_list_clusters", "search_weather_tool"]

agent = create_react_agent(model=local_llm, tools=tools)

# method to print the stream output
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        print("####### Printing Stream")
        if isinstance(message, tuple):
            print(f"####### message is : {message}")
        else:
            print("####### pretty print output:")
            message.pretty_print()

# # method to interact with llm
# def interact(user_input: str):
#     inputs = {"messages": [("user", user_input)]}
#     print_stream(graph.stream(inputs, stream_mode="values"))

# Update the new_interact function with a more explicit prompt
def new_interact(user_input: str):

    db_schema = '''
    The database consists of the following tables with their schema details:

    **Clusters Table:**
    - `tenantID_siteID` (HASH KEY, STRING) - Partition Key (Unique identifier for each Tenant).
    - `clusterID` (RANGE KEY, STRING) - Sort Key (unique itentifier for each user).
    - `available` (STRING) - availability status of the cluster.
    - `updatedAt` (STRING, TIMESTAMP) - last updated timestamp of the cluster status.
    - `clusterName` (STRING) - name of the cluster.

    **Instructions:**
    - Use this schema when answering queries.
    - When generating DynamoDB queries, ensure the correct use of Partition Keys (`HASH KEY`) and Sort Keys (`RANGE KEY`).
    '''


    template = '''

    Keep the following notes of the database schema in mind while answering the questions:

    {db_schema}


    Answer the following questions as best you can with the give tools. You have access to the following tools:

    {tools}

    
    IMPORTANT INSTRUCTIONS:

    1. For database queries about filters applied to clusters clusters, ALWAYS use and INVOKE the construct_filter_for_list_clusters tool.

    2. When using construct_filter_for_list_clusters, follow these rules:
    - Use attribute parameter for the field name (e.g., "clusterName"). if not required, set it to empty string
    - Use value parameter for the value to match (e.g., "st0322"). If not required, set it to empty string
    - Use limit parameter for maximum results (e.g., 10 or None for all)
    Examples:
    - To find clusters with name "st0322": attribute="clusterName", value="st0322", limit=10
    - To find available clusters: attribute="available", value="true", limit=10

    NEVER try to use Attr() expressions directly in your parameters!

    If the query isnt answerable using the given tools, please respond with "I don't have information on that."

    **IMPORTANT**: please stick to the above set of rules and do not deviate from them.

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action (proper parameters as described above)
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:'''

    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(db_schema=db_schema, tools=tools, tool_names=tool_names, input = user_input, agent_scratchpad = "scratchpad work for agent thinking process:")

    inputs = {"messages": [("user", formatted_prompt)]}
    print_stream(agent.stream(inputs, stream_mode="values"))

# Example interaction
# new_interact("What's the weather today?")
# new_interact("Tell me a joke")
new_interact("list all clusters with clusterName devex4")
# new_interact("list any 5 clusters")


# # Notes:
# system prompt extra information:
# with key being the attribute name and value being the condition as such for example Attr("attribute name")."condition"("value") where condition can be eq for equals, gt for greaterthan and lt for lessthan. 
#         some example filters are:
#         - filter = {"updatedAt": Attr("updatedAt").lt("2023-10-01T00:00:00Z")} this indicates that we want to filter the items where the updatedAt attribute is less than "2023-10-01T00:00:00Z".
#         - filter = {"available": Attr("available").eq("true")} this indicates that we want to filter the items where the available attribute is equal to "true".
#         - filter = {"available": Attr("available").eq("true"), "updatedAt": Attr("updatedAt").lt("2023-10-01T00:00:00Z")} this indicates that we want to filter the items where the available attribute is equal to "true" and the updatedAt attribute is less than "2023-10-01T00:00:00Z".