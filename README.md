# Ollama Chat App

A sophisticated chat application built with Python that leverages Ollama and LangChain for intelligent conversations, particularly focused on coding and software development assistance.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)

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
   git clone https://github.com/TanmaySinha2711/ollama-chat-app
   cd ollama-chat-app
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Ollama:
   - Download Ollama from [Ollama's official website](https://ollama.com/download)
   - Install the application
   - Start Ollama service
   - Pull the required model:
     ```bash
     ollama pull deepseek-coder-v2:16b
     ```

## Running the App

- Ensure Ollama is running in the background
- Start the Streamlit application:
  ```bash
  streamlit run frontend.py
  ```
- The application will automatically open in your default web browser. If it doesn't, you can access it at:
  - Local URL: [http://localhost:8501](http://localhost:8501)

## Usage

- **Starting a New Chat**:
  - Click the "New Chat" button in the sidebar
  - Type your message in the input box at the bottom
  - Press Enter or click the send button to submit
- **Managing Chat Sessions**:
  - View all your chat sessions in the sidebar
  - Click on any previous chat to continue the conversation
  - Chat history is automatically saved
- **Working with Code**:
  - Code snippets are automatically formatted with syntax highlighting
  - Use the copy button to copy code to clipboard
  - Download code files when available

## Troubleshooting

If you encounter any issues:

1. Check if Ollama is running:
   ```bash
   ollama list
   ```
   Ensure the `deepseek-coder-v2:16b` model is downloaded.

2. Verify port availability:
   - Make sure port 8501 is not in use.
   - If needed, you can specify a different port:
     ```bash
     streamlit run frontend.py --server.port 8502
     ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.