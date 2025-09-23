from google import genai

# Initialize client with your API key
client = genai.Client(api_key="AIzaSyAUyA7U5fxB77Sy678wBkFviiLwynOzoLI")

def chat_with_google(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-pro",  # Google Gemini model
        contents=prompt
    )
    return response.text

# Chat loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break
    answer = chat_with_google(user_input)
    print("Bot:", answer)

