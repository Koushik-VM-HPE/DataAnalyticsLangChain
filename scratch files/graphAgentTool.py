# status: Failure attempt to build a langgraph agent tool integration


# import operator, os
# from datetime import datetime
# from typing import Annotated, TypedDict, Union

# from dotenv import load_dotenv
# from langchain import hub
# from langchain.agents import create_react_agent
# from langchain_community.chat_models import ChatOllama
# from langchain_core.agents import AgentAction, AgentFinish
# from langchain_core.messages import BaseMessage
# from langchain_core.tools import tool
# from langgraph.graph import END, StateGraph
# from langchain_ollama.llms import OllamaLLM
# from langgraph.prebuilt import ToolNode

# from langchain_core.prompts.base import BasePromptTemplate
# from langchain_core.prompt_values import PromptValue
# from langchain_core.prompts import PromptTemplate

# # load_dotenv()
# # langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
# # langsmith_endpoint = os.getenv('LANGSMITH_ENDPOINT')

# @tool
# def get_now(format: str = "%Y-%m-%d %H:%M:%S"):
#     """
#     Get the current time
#     """
#     return datetime.now().strftime(format)


# tools = [get_now]

# tool_executor = ToolNode(tools)

# class AgentState(TypedDict):
#     input: str
#     chat_history: list[BaseMessage]
#     agent_outcome: Union[AgentAction, AgentFinish, None]
#     intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


# # class CustomPromptTemplate(BasePromptTemplate):
# #     def __init__(self, template: str, input_variables: list):
# #         self.template = template
# #         self.input_variables = input_variables

# #     def format(self, **kwargs) -> str:
# #         return self.template.format(**kwargs)

# #     def format_prompt(self, **kwargs) -> PromptValue:
# #         formatted_text = self.format(**kwargs)
# #         return PromptValue(text=formatted_text)

# promptString = """Answer the following questions as best you can. You have access to the following tools:

# {tools}

# Use the following format:

# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# Begin!

# Question: {input}
# Thought:{agent_scratchpad}"""
# prompt = PromptTemplate(template=promptString, input_variables=["tools", "tool_names", "input", "agent_scratchpad"])

# model = OllamaLLM(model="deepseek-r1:7b")
# # from langchain import hub
# # prompt = hub.pull("hwchase17/react")


# agent_runnable = create_react_agent(model, tools, prompt)

# def execute_tools(state):
#     print("Called `execute_tools`")
#     messages = [state["agent_outcome"]]
#     last_message = messages[-1]

#     tool_name = last_message.tool

#     print(f"Calling tool: {tool_name}")

#     action = ToolNode(
#         tools=tool_name,
#         # tool_input=last_message.tool_input,
#     )
#     response = tool_executor.invoke(action)
#     return {"intermediate_steps": [(state["agent_outcome"], response)]}


# def run_agent(state):
#     """
#     #if you want to better manages intermediate steps
#     inputs = state.copy()
#     if len(inputs['intermediate_steps']) > 5:
#         inputs['intermediate_steps'] = inputs['intermediate_steps'][-5:]
#     """
#     agent_outcome = agent_runnable.invoke(state)
#     return {"agent_outcome": agent_outcome}


# def should_continue(state):
#     messages = [state["agent_outcome"]]
#     last_message = messages[-1]
#     if "Action" not in last_message.log:
#         return "end"
#     else:
#         return "continue"
    
# workflow = StateGraph(AgentState)

# workflow.add_node("agent", run_agent)
# workflow.add_node("action", execute_tools)


# workflow.set_entry_point("agent")

# workflow.add_conditional_edges(
#     "agent", should_continue, {"continue": "action", "end": END}
# )


# workflow.add_edge("action", "agent")
# app = workflow.compile()

# input_text = "Whats the current time?"


# # inputs = {"input": input_text, "chat_history": []}
# results = []

# for event in app.stream({"input": input}, stream_mode="messages"):
#     print(event)


# # for s in app.stream(inputs):
# #     result = list(s.values())[0]
# #     results.append(result)
# #     print(result)
