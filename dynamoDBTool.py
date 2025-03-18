from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.output_parsers import JsonOutputParser, JsonOutputKeyToolsParser
from langchain.agents.output_parsers.json import JSONAgentOutputParser
from langchain.tools import tool
from langchain_ollama.llms import OllamaLLM
from langgraph.prebuilt import ToolNode
import boto3
from boto3.dynamodb.conditions import Key, And
import os, json
import pandas as pd

# Initialize the Ollama LLM
llm = OllamaLLM(model="deepseek-r1:7b")

# Initialize DynamoDB client
dynamodb_client = boto3.resource(
    'dynamodb',
    aws_access_key_id="AKIAWA33VBQEZCMFNKWP",
    aws_secret_access_key="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",
    # TODO: remove the following 
    # integ keys
    # aws_access_key_id="AKIA2I6HKRSFKNSP35XH",
    # aws_secret_access_key="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",
    # region_name="us-west-2"
    region_name="us-east-1"
)

# def list_users(user_id: str):
#     """Fetches all users for a given UserID sorted by CreatedAt."""


def list_clusters(table, limit, hash_key_name, hash_key_value, range_key_name=None, range_key_value=None):
    """
    Fetches clusters from the DynamoDB table based on a hash key.
    If a range key is provided, it adds it as a filter.

    :param table: DynamoDB table object.
    :param hash_key_name: Name of the hash key column.
    :param hash_key_value: The value to filter by for the hash key.
    :param range_key_name: (Optional) Name of the range key column.
    :param range_key_value: (Optional) The value to filter by for the range key.
    :return: List of matching items.
    """
    try:
        # Base condition (hash key)
        key_condition = Key(hash_key_name).eq(hash_key_value)

        # Add range key condition if provided
        if range_key_name and range_key_value:
            key_condition = And(key_condition, Key(range_key_name).eq(range_key_value))

        # Query DynamoDB
        response = table.query(
            KeyConditionExpression=key_condition,
            Limit=limit
        )

        return response.get("Items", [])

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


cluster_table = dynamodb_client.Table("devex_ocm_dev")  # Replace with your table name
cluster_table_hash_key = "tenantID_siteID"
cluster_table_range_key = "clusterID"
# print(list_clusters(table=cluster_table, limit=5, hash_key_name="tenantID_siteID", hash_key_value="c96iblviqa4b4joq1f2g_e1d8cecd-a7fb-45fb-a245-965e0f961ff6"))


@tool
def list_clusters_tool(hash_value: str) -> str:
    """
    LangChain tool that retrieves clusters from DynamoDB for a given hashkey.
     Args:
        hash_value (str): A unique identifier (e.g., hash) used to find relevant clusters.

    Returns:
        str: JSON string representing the clusterinfo, and its attributes
    """
    # clusters = list_clusters(table=cluster_table, hash_key_name=cluster_table_hash_key, hash_key_value=hash_value, limit=2)
    # print("clusters list obtained")
    # print(str(clusters))
    # print("##############")
    # return str(clusters) if clusters else "No clusters found for this hash key."
    # return {
    #   "action": "Final Answer",
    #   "action_input": "[{'clusterName': 'devex1', 'version': 'V1', 'available': 'True', 'siteID': 'e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'generation': Decimal('0'), 'status': 'Ready', 'tenantID': 'c96iblviqa4b4joq1f2g', 'createdAt': None, 'clusterID': '92dfb1dd-02ac-49e9-a608-7ce6ed2f959e', 'labels': {'feature.open-cluster-management.io/addon-config-policy-controller': 'available', 'feature.open-cluster-management.io/addon-governance-policy-framework': 'available', 'site-id': 'site1', 'cluster.open-cluster-management.io/clusterset': 'managed-clusters-region-a', 'demo': 'test', 'tenant-id': 'tenant123', 'cluster-id': 'dummyid1'}, 'updatedAt': '2023-03-16 12:47:16 +0530 IST', 'description': None, 'hubAccepted': 'True', 'tenantID_siteID': 'c96iblviqa4b4joq1f2g_e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'joined': 'True', 'type': 'ocmCluster'}, {'clusterName': 'devex4', 'version': 'V1', 'available': 'True', 'siteID': 'e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'generation': Decimal('0'), 'tenantID': 'c96iblviqa4b4joq1f2g', 'status': 'Ready', 'createdAt': None, 'clusterID': 'fde3935c-293c-42b1-9eae-1e8f2940820b', 'labels': {'feature.open-cluster-management.io/addon-config-policy-controller': 'available', 'feature.open-cluster-management.io/addon-governance-policy-framework': 'available', 'site-id': 'site4', 'cluster.open-cluster-management.io/clusterset': 'managed-clusters-region-b', 'demo': 'test', 'tenant-id': 'tenant874', 'cluster-id': 'cluster1238'}, 'updatedAt': '2023-03-16 12:57:54 +0530 IST', 'description': None, 'hubAccepted': 'True', 'tenantID_siteID': 'c96iblviqa4b4joq1f2g_e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'joined': 'True', 'type': 'ocmCluster'}]"
    # }
    return json.dumps({'clusterName': 'devex1', 'version': 'V1', 'available': 'True', 'siteID': 'e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'status': 'Ready', 'tenantID': 'c96iblviqa4b4joq1f2g', 'createdAt': None, 'clusterID': '92dfb1dd-02ac-49e9-a608-7ce6ed2f959e', 'labels': {'feature.open-cluster-management.io/addon-config-policy-controller': 'available', 'feature.open-cluster-management.io/addon-governance-policy-framework': 'available', 'site-id': 'site1', 'cluster.open-cluster-management.io/clusterset': 'managed-clusters-region-a', 'demo': 'test', 'tenant-id': 'tenant123', 'cluster-id': 'dummyid1'}, 'updatedAt': '2023-03-16 12:47:16 +0530 IST', 'description': None, 'hubAccepted': 'True', 'tenantID_siteID': 'c96iblviqa4b4joq1f2g_e1d8cecd-a7fb-45fb-a245-965e0f961ff6', 'joined': 'True', 'type': 'ocmCluster'})


# # Initialize an OpenAI-powered agent
# llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# output_parser = JsonOutputKeyToolsParser()

# # Create an agent that can use the tool
# agent = AgentExecutor.from_agent_and_tools(
#     tools=[list_clusters_tool],
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Agent type that chooses tools dynamically
#     # output_parser=output_parser
# )
agent = initialize_agent(
    tools=[list_clusters_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Agent type that chooses tools dynamically
    verbose=True,
    # output_parser=output_parser
)

# print(list_clusters_tool.invoke({"hash_value": "ciervhp6qrc3b27mmsa1_cc2fa1db-15da-4ba6-894c-d2accc2ac285"}))

# agent_executor = ToolNode(llm=llm, tools=[list_clusters_tool])
# Example Usage: Ask the agent to list users
response = agent.invoke({"input": "output full cluster info that u get from DB call as it is from the DB for 2 clusters with hashkey ciervhp6qrc3b27mmsa1_cc2fa1db-15da-4ba6-894c-d2accc2ac285"})
# response = agent.run("list clustersName for the hashkey ciervhp6qrc3b27mmsa1_cc2fa1db-15da-4ba6-894c-d2accc2ac285")

# print(response)
