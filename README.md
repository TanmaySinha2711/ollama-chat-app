# Ollama Chat App

A sophisticated chat application built with Python that leverages Ollama and LangChain for intelligent conversations, particularly focused on coding and software development assistance.

## Features

- **Interactive Chat Interface**: Built with Streamlit for a clean, user-friendly experience
- **Code-Aware Responses**: Uses the deepseek-coder-v2:16b model for specialized coding assistance
- **Chat History Management**: Maintains conversation history with automatic summarization
- **Smart Title Generation**: Automatically generates relevant titles for chat sessions
- **Code Block Handling**: 
  - Syntax highlighting for multiple programming languages
  - Copy-to-clipboard functionality
  - Code download options with appropriate file extensions
- **Session Management**:
  - Multiple chat sessions support
  - Automatic cleanup of old sessions
  - Chat history persistence

## Requirements

- Python 3.x
- Ollama >= 0.1.4
- Streamlit >= 1.29.0
- LangChain >= 0.1.0
- LangChain-community >= 0.0.10

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/ollama-chat-app.git
cd ollama-chat-app
```
