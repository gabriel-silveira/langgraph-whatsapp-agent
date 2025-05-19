import logging
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver

LOGGER = logging.getLogger("whatsapp")


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

memory = MemorySaver()

llm = init_chat_model(
    model_provider="openai",
    model="gpt-4o-mini",
    temperature=0.7,
)

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [{"role": "assistant", "content": response.content}]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)


def answer(user_input: str, thread_id: str):
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config={"configurable": {"thread_id": thread_id}}
    )

    # Obtém a última mensagem do resultado
    last_message = result["messages"][-1]

    # Retorna o conteúdo da mensagem
    return last_message.content


# thread_id = "987654321"
#
# if __name__ == "__main__":
#     while True:
#         try:
#             user_input = input("\nUser: ")
#
#             if user_input.lower() in ["exit", "quit", "q"]:
#                 print("Goodbye!")
#                 break
#
#             response = answer(user_input, thread_id)
#
#             print(f"\nAssistant: {response}")
#         except:
#             # fallback if input() is not available
#             user_input = "What do you know about LangGraph?"
#
#             print(f"\nUser: {user_input}")
#
#             response = answer(user_input, thread_id)
#
#             print(f"\nAssistant: {response}")
#
#             break