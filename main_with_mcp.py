import asyncio
from src.agents.base.graph import build_agent


async def main():
    async with build_agent() as graph:
        while True:
            try:
                # Get user input
                user_message = input("You: ")
                
                if user_message.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                # Process the message through the graph
                response = graph.invoke({
                    "messages": [{"role": "user", "content": user_message}]
                })
                
                # Get the last assistant message
                for message in response['messages']:
                    if hasattr(message, 'content') and message.content and hasattr(message, 'name') and message.name == 'supervisor':
                        print(f"Assistant: {message.content}")
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                break

if __name__ == "__main__":
    asyncio.run(main())
