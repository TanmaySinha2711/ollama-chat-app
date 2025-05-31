import gradio as gr
from langchain_ollama import ChatOllama
from config import Config
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Initialize model
model = ChatOllama(model=Config.DEFAULT_MODEL)

# Simple chat function with history support
def answer(message, history):
    # Regular text query
    query = message if isinstance(message, str) else message["text"]
    
    # Create messages list with system message
    messages = [SystemMessage(content=Config.SYSTEM_MESSAGE)]
    
    # Add conversation history
    for h in history:
        # When using type="messages", history items are dictionaries with 'role' and 'content' keys
        if isinstance(h, dict):
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            elif h["role"] == "assistant":
                messages.append(AIMessage(content=h["content"]))
        # For backward compatibility with tuple format
        elif isinstance(h, (list, tuple)) and len(h) == 2:
            user_msg, assistant_msg = h
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=assistant_msg))
    
    # Add current user message
    messages.append(HumanMessage(content=query))
    
    # Generate response using the full conversation context
    response = model.invoke(messages)
    return response.content

# Create the Gradio interface
demo = gr.ChatInterface(
    answer,
    chatbot=gr.Chatbot(height=600, type="messages"),
    textbox=gr.Textbox(placeholder="Type a message"),
    title="Ollama Chatbot",
    description="Chat with the Ollama model.",
    examples=["What can you help me with?", "Tell me about coding best practices"],
    cache_examples=False,
    theme="soft"
)

# Launch the app
if __name__ == "__main__":
    demo.launch()