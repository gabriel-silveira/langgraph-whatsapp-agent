from src.chatbot.stream import answer


thread_id = "ABCDEFGH"

if __name__ == "__main__":
    while True:
        try:
            user_input = input("\nUser: ")

            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            response = answer(user_input, thread_id)

            print(f"\nAssistant: {response}")
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"

            print(f"\nUser: {user_input}")

            response = answer(user_input, thread_id)

            print(f"\nAssistant: {response}")

            break