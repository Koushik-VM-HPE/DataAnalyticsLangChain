from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langgraph.graph import END, StateGraph, START, Graph
from langgraph.graph.message import AnyMessage, add_messages
from typing_extensions import TypedDict
from typing import Annotated, Literal
# from IPython.display import Image, display
import random

"""
Ref - https://medium.com/ai-agents/langgraph-for-beginners-part-3-conditional-edges-16a3aaad9f31
VERY Basic LangGraph implementation
"""
"""
def weather(str):
  return "Hi! Well.. I have no idea... But... "

# Define a node that returns rainy weather
def rainy_weather(str):
  return str + " Its going to rain today. Carry an umbrella."

# Define a node that returns sunny weather
def sunny_weather(str):
  return str + " Its going to be sunny today. Wear sunscreen."

def forecast_weather(str)->Literal["rainy", "sunny"]:
  if random.random() < 0.5:
    return "rainy"
  else:
    return "sunny"

workflow = Graph()
workflow.add_node("weather", weather)
workflow.add_node("rainy", rainy_weather)
workflow.add_node("sunny", sunny_weather)
workflow.add_edge(START, "weather")

workflow.add_conditional_edges("weather", forecast_weather)
workflow.add_edge("rainy", END)
workflow.add_edge("sunny", END)
app = workflow.compile()

print(app.invoke('Hi! What does the weather look like? '))
print(app.invoke("How much is 2+2"))

"""

"""
Ref - https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot
Basic Chatbot implementation
"""

# Define the state for the agent
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# Initialize OllamaLLM with the "deepseek-r1:7b" model
llm = OllamaLLM(model="deepseek-r1:7b")


graph_builder = StateGraph(State)


def chatbot(state: State):
  return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

def stream_graph_updates(user_inp: str):
  for event in graph.stream({"messages": [{"role": "user", "content": user_inp}]}):
    for value in event.values():
      print("Assistant:", value["messages"][-1])

if __name__ == "__main__":
  while True:
    try:
      user_input = input("User: ")
      if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

      stream_graph_updates(user_input)
    except:
      # fallback if input() is not available
      user_input = "What do you know about LangGraph?"
      print("User: " + user_input)
      stream_graph_updates(user_input)
      break

# """